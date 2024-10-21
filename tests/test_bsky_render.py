import pytest

from src.core.bsky import BskyClient
from src.defs.render import HumanPost

client = BskyClient()
parse = lambda url: url.replace("https://bsky.app/profile/", "at://").replace(
    "post", "app.bsky.feed.post"
)


@pytest.mark.asyncio
class TestRender:
    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_text():
        await client.initialize()
        uri = parse("https://bsky.app/profile/bsky.app/post/3l6oveex3ii2l")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f is not None

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_image():
        uri = parse("https://bsky.app/profile/bsky.app/post/3l6dplwluhb2f")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert "Thanks everyone" in f.content
        assert f.images

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_video():
        uri = parse("https://bsky.app/profile/bsky.app/post/3l3wdzzedvv2y")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert "all-time peak!" in f.content
        assert f.video

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_gif():
        uri = parse("https://bsky.app/profile/sseabells.bsky.social/post/3l6xlh6w33v2y")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert "the iconic mint flossing gif here on bsky?" in f.content
        assert f.gif

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_reply_one():
        uri = parse("https://bsky.app/profile/bsky.app/post/3l4ch3gu65b2n")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert "1.91.1 is rolling out now" in f.content
        assert f.is_reply
        assert f.parent_post is not None
        assert "This update introduces" in f.parent_post.content

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_reply_thread():
        uri = parse("https://bsky.app/profile/bsky.app/post/3l6ovv5maiy2o")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content
        assert f.is_reply
        assert f.parent_post is not None
        assert f.parent_post.content
        assert f.parent_post.is_reply
        assert f.parent_post.parent_post is not None
        assert f.parent_post.parent_post.content
        assert f.parent_post.parent_post.is_reply

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_quote():
        uri = parse("https://bsky.app/profile/bsky.app/post/3l6sjdebqbx2q")
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert "congratulations" in f.content
        assert f.is_quote
        assert f.parent_post is not None
        assert "half a million new people" in f.parent_post.content

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_timeline():
        data = await client.client.get_timeline()
        posts = [HumanPost.parse(post) for post in data.feed]
        assert posts
