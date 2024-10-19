from persica.factory.component import AsyncInitializingComponent

from atproto import AsyncClient
from atproto.exceptions import BadRequestError

from src.config import config
from src.utils.log import logs
from src.utils.session_reuse import SessionReuse


class BskyClient(AsyncInitializingComponent):
    def __init__(self):
        self.client = AsyncClient()
        self.session = SessionReuse()
        self.client.on_session_change(self.session.on_session_change)

    async def initialize(self):
        session = self.session.get_session()
        if session:
            try:
                await self.client.login(session_string=session)
                logs.info(
                    "[bsky] Login with session success, me: %s", self.client.me.handle
                )
                return
            except BadRequestError:
                pass
        await self.client.login(config.bsky.username, config.bsky.password)
        logs.info(
            "[bsky] Login with username and password success, me: %s",
            self.client.me.handle,
        )
