from simplevk import Message
from src.epicnotify.bot import bot
from src.epicnotify.keyboards import MAIN_KEYBOARD, SUBSCRIBE_KEYBOARD


@bot.on.start()
def start_handler(message: Message):
    message.answer(
        "🎮 EpicNotify\n\n"
        "Я буду уведомлять вас о новых раздачах в Epic Games Store.\n"
        "Нажмите кнопку ниже или используйте /sub для подписки.",
        keyboard=MAIN_KEYBOARD,
    )
    message.answer("Настройка уведомлений:", keyboard=SUBSCRIBE_KEYBOARD)
