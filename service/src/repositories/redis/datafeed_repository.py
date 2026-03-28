from redis.asyncio import Redis

from domain.datafeed import DatafeedModel, PilotModel
from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface


class RedisDatafeedRepository(DatafeedRepositoryInterface):
    KEY = "vatsim:datafeed"
    CALLSIGNS_KEY = "vatsim:pilots"
    DATA_KEY = "vatsim:pilots:data"

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def update(self, feed: DatafeedModel) -> None:
        new_callsigns = {pilot.callsign for pilot in feed.pilots}

        existing = await self.redis.smembers(self.CALLSIGNS_KEY)
        existing = {v.decode() if isinstance(v, bytes) else v for v in existing}

        to_remove = existing - new_callsigns

        pipe = self.redis.pipeline()

        if to_remove:
            pipe.hdel(self.DATA_KEY, *to_remove)

        for pilot in feed.pilots:
            pipe.hset(
                self.DATA_KEY,
                pilot.callsign,
                pilot.model_dump_json(exclude_none=True, exclude_unset=True),
            )

        pipe.delete(self.CALLSIGNS_KEY)

        if new_callsigns:
            pipe.sadd(self.CALLSIGNS_KEY, *new_callsigns)

        await pipe.execute()

    async def has_callsign(self, callsign: str) -> bool:
        return bool(await self.redis.sismember(self.CALLSIGNS_KEY, callsign))

    async def get_pilot_data(self, callsign: str) -> PilotModel | None:
        raw = await self.redis.hget(self.DATA_KEY, callsign)

        if raw is None:
            return None

        if isinstance(raw, bytes):
            raw = raw.decode()

        return PilotModel.model_validate_json(raw)
