from cashews import cache

from src.defs.render import HumanPost


class PostCache:
    @staticmethod
    def key(post: HumanPost) -> str:
        key = post.cid
        if post.is_repost and post.parent_post:
            key = post.parent_post.cid
        return "post:" + key

    @staticmethod
    async def set(post: HumanPost):
        await cache.set(PostCache.key(post), "1", expire=60 * 60 * 24 * 7)

    @staticmethod
    async def get(post: HumanPost) -> bool:
        return await cache.get(PostCache.key(post)) is not None
