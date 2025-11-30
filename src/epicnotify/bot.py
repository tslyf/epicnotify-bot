from simplevk import Bot
from src.epicnotify.config import settings

bot = Bot(token=settings.vk_token, group_id=settings.group_id)
