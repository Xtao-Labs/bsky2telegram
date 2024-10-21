import asyncio
import traceback

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait

from src.config import config
from src.core.bsky import BskyClient
from src.defs.cache import PostCache
from src.defs.render import HumanPost
from src.utils.log import logs


def flood_wait():
    def decorator(function):
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except FloodWait as e:
                logs.warning(f"遇到 FloodWait，等待 {e.value} 秒后重试！")
                await asyncio.sleep(e.value + 1)
                return await wrapper(*args, **kwargs)
            except Exception as e:
                traceback.format_exc()
                raise e

        return wrapper

    return decorator


class Timeline:
    @staticmethod
    async def get_timeline(client: BskyClient) -> list[HumanPost]:
        posts = await client.client.get_timeline()
        data = []
        keys = []
        for post in posts.feed:
            try:
                d = HumanPost.parse(post)
                key = PostCache.key(d)
                if await PostCache.get(d) or key in keys:
                    continue
                data.append(d)
                keys.append(key)
            except Exception as e:
                print(e)
                logs.error(
                    "Error when parsing post: %s",
                    post.post.uri if post.post else str(e),
                )
        data.reverse()
        keys.clear()
        return data

    @staticmethod
    def get_button(post: HumanPost) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Source", url=post.url),
                    InlineKeyboardButton("Author", url=post.author.url),
                ]
            ]
        )

    @staticmethod
    def get_media_group(text: str, post: HumanPost) -> list[InputMediaPhoto]:
        data = []
        images = post.images
        for idx, image in enumerate(images):
            data.append(
                InputMediaPhoto(
                    image,
                    caption=text if idx == 0 else None,
                    parse_mode=ParseMode.HTML,
                )
            )
        return data

    @staticmethod
    def get_post_text(post: HumanPost) -> str:
        text = "<b>Bsky Timeline Update</b>\n\n<code>"
        text += post.content
        text += "</code>\n\n"
        key = "发表"
        if post.is_reply:
            key = "回复"
        elif post.is_quote:
            key = "引用"
        elif post.is_repost:
            text += f"{post.repost_info.by.format} 转发于 {post.repost_info.time_str}\n"
        text += f"{post.author.format} {key}于 {post.time_str}\n"
        text += f"点赞: {post.like_count} | 引用: {post.quote_count} | 回复: {post.reply_count} | 转发: {post.repost_count}"
        return text

    @staticmethod
    @flood_wait()
    async def send_to_user(bot: Client, post: HumanPost):
        text = Timeline.get_post_text(post)
        if post.gif:
            return await bot.send_animation(
                config.push.chat_id,
                post.gif,
                caption=text,
                reply_to_message_id=config.push.topic_id,
                parse_mode=ParseMode.HTML,
                reply_markup=Timeline.get_button(post),
            )
        elif not post.images:
            return await bot.send_message(
                config.push.chat_id,
                text,
                disable_web_page_preview=True,
                reply_to_message_id=config.push.topic_id,
                parse_mode=ParseMode.HTML,
                reply_markup=Timeline.get_button(post),
            )
        elif len(post.images) == 1:
            return await bot.send_photo(
                config.push.chat_id,
                post.images[0],
                caption=text,
                reply_to_message_id=config.push.topic_id,
                parse_mode=ParseMode.HTML,
                reply_markup=Timeline.get_button(post),
            )
        else:
            await bot.send_media_group(
                config.push.chat_id,
                Timeline.get_media_group(text, post),
                reply_to_message_id=config.push.topic_id,
            )

    @staticmethod
    async def send_posts(client: BskyClient, bot: Client):
        logs.info("Fetching posts to user...")
        posts = await Timeline.get_timeline(client)
        logs.info(f"Got {len(posts)} posts...Sending...")
        for post in posts:
            try:
                await Timeline.send_to_user(bot, post)
                await PostCache.set(post)
            except Exception as e:
                logs.error("Error when sending post: %s", str(e))
        logs.info("Sending posts to user done!")
