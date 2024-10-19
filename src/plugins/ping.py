from persica.factory.component import BaseComponent
from pyrogram import filters
from pyrogram.types import Message

from src.core.bot import TelegramBot


class PingBotPlugin(BaseComponent):
    def __init__(self, telegram_bot: TelegramBot):
        @telegram_bot.bot.on_message(filters=filters.command("ping_bsky"))
        async def ping(_, message: "Message"):
            await message.reply("pong")
