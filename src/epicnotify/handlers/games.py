from simplevk import Keyboard, Message

from src.epicnotify.bot import bot
from src.epicnotify.services.epic import get_free_games
from src.epicnotify.services.vk import format_game_msg, upload_photo_to_vk


@bot.on.command(name="list")
@bot.on.message(text=["игры", "список"])
@bot.on.message(payload={"command": "list"})
def list_games_handler(event: Message):
    active, upcoming = get_free_games()

    if not active and not upcoming:
        event.answer("😔 Сейчас нет активных раздач.")
        return

    for game in active + upcoming:
        attachment = upload_photo_to_vk(bot, game.image_url or "")
        kb = Keyboard(inline=True).add_openlink(game.url, "🔗 Забрать игру")
        intro = "🔥 АКТИВНАЯ РАЗДАЧА" if game in active else "🔜 СКОРО БУДЕТ"
        event.answer(
            f"{intro}\n\n{format_game_msg(game)}",
            attachment=[attachment] if attachment else None,
            keyboard=kb,
        )
