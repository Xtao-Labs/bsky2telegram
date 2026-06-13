from apscheduler.schedulers.asyncio import AsyncIOScheduler
from persica.factory.component import AsyncInitializingComponent


class TimeScheduler(AsyncInitializingComponent):
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")

    async def initialize(self):
        self.scheduler.start()

    async def shutdown(self):
        self.scheduler.shutdown()
