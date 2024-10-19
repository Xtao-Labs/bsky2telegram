from cashews import cache

from src.config import config
from persica.factory.component import AsyncInitializingComponent


class Cache(AsyncInitializingComponent):
    async def initialize(self):
        cache.setup(config.cache_uri)
