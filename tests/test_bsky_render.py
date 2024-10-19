import pytest

from src.core.bsky import BskyClient
from src.defs.render import HumanPost

client = BskyClient()
base_uri = "at://did:plc:sab4cdxxfyqjeh4pnfey23sh/app.bsky.feed.post/"


@pytest.mark.asyncio
class TestRender:
    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_text():
        await client.initialize()
        uri = base_uri + "3kjbatbj5kt2v"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f is not None

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_image():
        uri = base_uri + "3l6ucyxck372f"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content == "test1"
        assert f.images

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_video():
        uri = base_uri + "3l6ug2ighnk2a"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content == "ye!"
        assert f.video

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_gif():
        uri = base_uri + "3l6ug54iydf2e"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content == "what"
        assert f.gif

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_reply():
        uri = base_uri + "3l6ufasnzxe2k"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content == "test4"
        assert f.is_reply
        assert f.parent_post is not None

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_quote():
        uri = base_uri + "3l6ud27jp662q"
        e = await client.client.get_post_thread(uri)
        f = HumanPost.parse_thread(e.thread)
        assert f.content == "test2"
        assert f.is_quote
        assert f.parent_post is not None

    @staticmethod
    @pytest.mark.asyncio(scope="session")
    async def test_timeline():
        data = await client.client.get_timeline()
        posts = [HumanPost.parse(post) for post in data.feed]
        assert posts
