from redis.asyncio import Redis

from domain.datafeed import DatafeedModel
from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface


class RedisDatafeedRepository(DatafeedRepositoryInterface):
    KEY = "vatsim:datafeed"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self) -> DatafeedModel | None:
        raw = await self.redis.get(self.KEY)
        if raw is None:
            return None
        return DatafeedModel.model_validate_json(raw)

    async def update(self, feed: DatafeedModel) -> None:
        await self.redis.set(self.KEY, feed.model_dump_json())
