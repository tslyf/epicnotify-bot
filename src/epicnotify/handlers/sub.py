import logging

from simplevk import Message, MessageEvent

from src.epicnotify.bot import bot
from src.epicnotify.database import Chat
from src.epicnotify.keyboards import SUBSCRIBE_KEYBOARD, UNSUBSCRIBE_KEYBOARD
from src.epicnotify.services.vk import check_admin

logger = logging.getLogger("epicnotify")


@bot.on.command(name="sub")
@bot.on.message(payload={"cmd": "sub"})
@bot.on.message_event(payload={"cmd": "sub"})
def subscribe_handler(event: Message | MessageEvent):
    admin = check_admin(bot, event.peer_id, event.from_id)
    if admin is None:
        event.base_answer("⚡ Мне необходимы права администратора в беседе.")
        return
    elif not admin:
        event.base_answer("⛔ Только администраторы могут управлять подпиской.")
        return

    _, created = Chat.get_or_create(peer_id=event.peer_id)

    if created:
        action = event.edit if isinstance(event, MessageEvent) else event.answer
        action(
            "🔔 Теперь Вы будете получать уведомления о "
            "новых бесплатных играх Epic Games."
            "\n\n⚡ Чтобы отписаться, напишите /unsub",
            keyboard=UNSUBSCRIBE_KEYBOARD,
        )
    else:
        event.base_answer("🔔 Вы уже получаете уведомления.")


@bot.on.command(name="unsub")
@bot.on.message(payload={"cmd": "unsub"})
@bot.on.message_event(payload={"cmd": "unsub"})
def unsubscribe_handler(event: Message | MessageEvent):
    admin = check_admin(bot, event.peer_id, event.from_id)
    if admin is None:
        event.base_answer("⚡ Мне необходимы права администратора в беседе.")
        return
    elif not admin:
        event.base_answer("⛔ Только администраторы могут управлять подпиской.")
        return

    deleted = Chat.delete().where(Chat.peer_id == event.peer_id).execute()

    if deleted:
        action = event.edit if isinstance(event, MessageEvent) else event.answer
        action(
            (
                "🔕 Вы отписались от уведомлений."
                "\n\n⚡ Чтобы заново подписаться, напишите /sub"
            ),
            keyboard=SUBSCRIBE_KEYBOARD,
        )
    else:
        event.base_answer("🔕 Вы не подписаны на уведомления.")
