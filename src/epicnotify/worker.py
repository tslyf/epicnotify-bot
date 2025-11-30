import logging
import time

from peewee import Tuple
from simplevk import Keyboard

from src.epicnotify.bot import bot
from src.epicnotify.database import Chat, Notified
from src.epicnotify.services.epic import get_free_games
from src.epicnotify.services.vk import format_game_msg, upload_photo_to_vk

logger = logging.getLogger("epicnotify")


def worker_loop():
    logger.info("Worker loop started")
    while True:
        try:
            active_games, _ = get_free_games()

            already_notified = [
                i.game_id
                for i in Notified.select(Notified.game_id)
                .where(
                    Tuple(Notified.game_id, Notified.start_date).in_([
                        (i.id, i.start_date) for i in active_games
                    ])
                )
                .execute()
            ]
            active_games = [i for i in active_games if i.id not in already_notified]

            Notified.insert_many(
                [(i.id, i.start_date) for i in active_games],
                [Notified.game_id, Notified.start_date],
            ).execute()

            peer_ids = [i.peer_id for i in Chat.select(Chat.peer_id).execute()]

            if not peer_ids:
                continue

            for game in active_games:
                logger.info(
                    f"Notifying about game {game.title} ({game.id}) to {len(peer_ids)} chats"
                )
                attachment = upload_photo_to_vk(bot, game.image_url or "")
                msg_text = f"🎁 Новая бесплатная игра!\n\n{format_game_msg(game)}"
                keyboard = Keyboard(inline=True).add_openlink(
                    game.url, "🔗 Забрать игру"
                )
                try:
                    bot.sent.send_many(
                        peer_ids=peer_ids,
                        message=msg_text,
                        attachment=[attachment] if attachment else None,
                        keyboard=keyboard,
                    )
                except Exception:
                    logger.exception("Failed to send message")

        except Exception:
            logger.exception("Worker loop error")

        finally:
            time.sleep(5 * 60)
