from asyncio import Lock

from persica.factory.component import BaseComponent
from pyrogram import Client, filters
from pyrogram.types import Message

from src.config import config
from src.core.bot import TelegramBot
from src.core.bsky import BskyClient
from src.core.scheduler import TimeScheduler
from src.defs.timeline import Timeline

_lock = Lock()


async def update_all(client: BskyClient, bot: Client, message: Message):
    if _lock.locked():
        await message.reply("正在检查更新，请稍后再试！")
        return
    async with _lock:
        msg = await message.reply("开始检查更新！")
        await Timeline.send_posts(client, bot)
        await msg.edit("检查更新完毕！")


class UpdateBotPlugin(BaseComponent):
    def __init__(
        self, telegram_bot: TelegramBot, client: BskyClient, scheduler: TimeScheduler
    ):
        @telegram_bot.bot.on_message(
            filters=filters.command("check_update_bsky")
            & filters.user(config.bot.owner)
        )
        async def _update_all(_, message: "Message"):
            await update_all(client, telegram_bot.bot, message)

        @scheduler.scheduler.scheduled_job(
            "cron", hour="*", minute="*", second="0", id="update_all"
        )
        async def update_all_1_minutes():
            if _lock.locked():
                return
            async with _lock:
                await Timeline.send_posts(client, telegram_bot.bot)
