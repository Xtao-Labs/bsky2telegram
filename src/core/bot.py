from persica.factory.component import AsyncInitializingComponent

from pyrogram import Client

from src.config import config
from src.utils.log import logs


class TelegramBot(AsyncInitializingComponent):
    def __init__(self):
        self.bot = Client(
            "bot",
            api_id=config.bot.api_id,
            api_hash=config.bot.api_hash,
            bot_token=config.bot.token,
            workdir="data",
        )

    async def initialize(self):
        await self.bot.start()
        logs.info(f"Telegram bot started, As @{self.bot.me.username}")

    async def shutdown(self):
        try:
            await self.bot.stop()
        except RuntimeError:
            pass
