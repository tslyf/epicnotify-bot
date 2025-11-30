from simplevk import ButtonColor, Keyboard

MAIN_KEYBOARD = Keyboard().add_text("🎮 Бесплатные игры", payload={"command": "list"})
SUBSCRIBE_KEYBOARD = Keyboard(inline=True).add_callback(
    "Подписаться", payload={"cmd": "sub"}, color=ButtonColor.POSITIVE
)
UNSUBSCRIBE_KEYBOARD = Keyboard(inline=True).add_callback(
    "Отписаться", payload={"cmd": "unsub"}, color=ButtonColor.NEGATIVE
)
