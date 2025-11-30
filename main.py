import logging
from threading import Thread

import src.epicnotify.handlers.common  # noqa: F401
import src.epicnotify.handlers.games  # noqa: F401
import src.epicnotify.handlers.sub  # noqa: F401
from src.epicnotify.bot import bot
from src.epicnotify.database import init_db
from src.epicnotify.worker import worker_loop

init_db()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    Thread(target=worker_loop, daemon=True).start()

    bot.start_listen()
