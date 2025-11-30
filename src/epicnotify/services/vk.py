import logging
import threading
from datetime import datetime, timezone
from io import BytesIO

import requests
from cachebox import TTLCache, cached
from simplevk import Bot
from vk_api import VkTools

from src.epicnotify.database import CachedImage
from src.epicnotify.services.epic import Game
from src.epicnotify.utils import seconds_to_string

logger = logging.getLogger("epicnotify")

_url_locks: dict[str, threading.Lock] = {}
_locks_mutex = threading.Lock()


def _get_lock_for_url(url: str) -> threading.Lock:
    with _locks_mutex:
        if url not in _url_locks:
            _url_locks[url] = threading.Lock()
        return _url_locks[url]


def upload_photo_to_vk(bot: Bot, url: str) -> str | None:
    if not url:
        return None

    try:
        cached: CachedImage | None = CachedImage.get_or_none(
            CachedImage.image_url == url
        )
        if cached:
            return str(cached.attachment)
    except Exception:
        pass

    lock = _get_lock_for_url(url)
    with lock:
        try:
            cached = CachedImage.get_or_none(
                CachedImage.image_url == url
            )
            if cached:
                return str(cached.attachment)
        except Exception:
            pass

        try:
            img_resp = requests.get(url, timeout=10)
            img_resp.raise_for_status()
            image_data = BytesIO(img_resp.content)
            image_data.name = "image.png"
            image_data.seek(0)
        except Exception:
            logger.exception(f"Failed to download image {url}")
            return None

        try:
            # TODO: стоило бы явно указывать peer_id
            photo = bot.uploader.photo_messages(photos=image_data)[0]
            attachment = f"photo{photo['owner_id']}_{photo['id']}"

            CachedImage.create(image_url=url, attachment=attachment)

            return attachment
        except Exception:
            logger.exception(f"Failed to upload image {url} to VK")
            return None


def format_game_msg(game: Game) -> str:
    now = datetime.now(timezone.utc)

    if game.is_active:
        delta = (game.end_date - now).total_seconds()
        time_str = f"📅 Завершение через {seconds_to_string(delta)}"
    else:
        delta = (game.start_date - now).total_seconds()
        time_str = f"⏱️ Начало через {seconds_to_string(delta)}"

    price_block = f"💰 {game.fmt_price_discount} / {game.fmt_price_original}"
    description = game.description[:300] if game.description else ""
    if description and len(description) < len(game.description or ""):
        description += "..."

    return (
        f"🎮 {game.title}\n"
        + f"{price_block}\n\n"
        + (f"📝 {description}\n\n" if description else "")
        + time_str
    )


@cached(
    TTLCache(maxsize=1000, ttl=30),
    key_maker=lambda args, kwargs: (kwargs.get("peer_id") or args[1]),
)
def get_chat_admins(bot: Bot, peer_id: int) -> set[int] | None:
    admins = set()

    try:
        tools = VkTools(bot.session)
        all_members = tools.get_all(
            method="messages.getConversationMembers",
            max_count=200,
            values={"peer_id": peer_id},
        )

        items = all_members.get("items", [])

        for member in items:
            member_id = member.get("member_id")
            if member.get("is_admin") or member.get("is_owner"):
                admins.add(member_id)

    except Exception as e:
        logger.warning(f"Failed to get conversation members for {peer_id}: {e}")
        return None

    return admins


def check_admin(bot: Bot, peer_id: int, user_id: int) -> bool | None:
    if peer_id == user_id:
        return True

    admins = get_chat_admins(bot, peer_id)
    return user_id in admins if admins is not None else None
