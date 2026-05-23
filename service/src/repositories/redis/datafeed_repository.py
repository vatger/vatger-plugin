import logging

from redis.asyncio import Redis

from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface
from models.datafeed import ControllerModel, DatafeedModel, PilotModel

logger = logging.getLogger(__name__)


class RedisDatafeedRepository(DatafeedRepositoryInterface):
    KEY = "vatsim:datafeed"
    CALLSIGNS_SET_KEY = "vatsim:pilots"
    PILOTS_DATA_KEY = "vatsim:pilots:data"
    PILOTS_CID_KEY = "vatsim:pilots:cid"  # hash: cid -> callsign
    CONTROLLERS_SET_KEY = "vatsim:controllers"
    CONTROLLERS_DATA_KEY = "vatsim:controllers:data"
    CONTROLLERS_CID_KEY = "vatsim:controllers:cid"  # hash: cid -> callsign

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def update(self, feed: DatafeedModel) -> None:
        pipe = self.redis.pipeline()

        await self._update_pilots(feed, pipe)
        await self._update_controllers(feed, pipe)

        await pipe.execute()

    async def _update_pilots(self, feed: DatafeedModel, pipe) -> None:
        new_callsigns = {pilot.callsign for pilot in feed.pilots}

        existing = await self.redis.smembers(self.CALLSIGNS_SET_KEY)
        existing = {v.decode() if isinstance(v, bytes) else v for v in existing}

        to_remove = existing - new_callsigns

        if to_remove:
            pipe.hdel(self.PILOTS_DATA_KEY, *to_remove)

            existing_cid_map = await self.redis.hgetall(self.PILOTS_CID_KEY)
            stale_cids = [
                cid
                for cid, callsign in existing_cid_map.items()
                if (callsign.decode() if isinstance(callsign, bytes) else callsign) in to_remove
            ]
            if stale_cids:
                pipe.hdel(self.PILOTS_CID_KEY, *stale_cids)

        for pilot in feed.pilots:
            pipe.hset(
                self.PILOTS_DATA_KEY,
                pilot.callsign,
                pilot.model_dump_json(exclude_none=True, exclude_unset=True),
            )
            pipe.hset(self.PILOTS_CID_KEY, str(pilot.cid), pilot.callsign)

        pipe.delete(self.CALLSIGNS_SET_KEY)

        if new_callsigns:
            pipe.sadd(self.CALLSIGNS_SET_KEY, *new_callsigns)

    async def _update_controllers(self, feed: DatafeedModel, pipe) -> None:
        new_callsigns = {controller.callsign for controller in feed.controllers}

        existing = await self.redis.smembers(self.CONTROLLERS_SET_KEY)
        existing = {v.decode() if isinstance(v, bytes) else v for v in existing}

        to_remove = existing - new_callsigns

        if to_remove:
            pipe.hdel(self.CONTROLLERS_DATA_KEY, *to_remove)

            existing_cid_map = await self.redis.hgetall(self.CONTROLLERS_CID_KEY)
            stale_cids = [
                cid
                for cid, callsign in existing_cid_map.items()
                if (callsign.decode() if isinstance(callsign, bytes) else callsign) in to_remove
            ]
            if stale_cids:
                pipe.hdel(self.CONTROLLERS_CID_KEY, *stale_cids)

        for controller in feed.controllers:
            pipe.hset(
                self.CONTROLLERS_DATA_KEY,
                controller.callsign,
                controller.model_dump_json(exclude_none=True, exclude_unset=True),
            )
            pipe.hset(self.CONTROLLERS_CID_KEY, str(controller.cid), controller.callsign)

        pipe.delete(self.CONTROLLERS_SET_KEY)

        if new_callsigns:
            pipe.sadd(self.CONTROLLERS_SET_KEY, *new_callsigns)

    async def has_pilot(self, callsign: str) -> bool:
        return bool(await self.redis.sismember(self.CALLSIGNS_SET_KEY, callsign))

    async def get_pilot_by_callsign(self, callsign: str) -> PilotModel | None:
        raw = await self.redis.hget(self.PILOTS_DATA_KEY, callsign)
        return self._decode_model(raw, PilotModel)

    async def get_pilot_by_cid(self, cid: int) -> PilotModel | None:
        callsign = await self.redis.hget(self.PILOTS_CID_KEY, str(cid))
        if callsign is None:
            return None
        if isinstance(callsign, bytes):
            callsign = callsign.decode()
        return await self.get_pilot_by_callsign(callsign)

    async def has_controller(self, callsign: str) -> bool:
        return bool(await self.redis.sismember(self.CONTROLLERS_SET_KEY, callsign))

    async def get_controller_by_callsign(self, callsign: str) -> ControllerModel | None:
        raw = await self.redis.hget(self.CONTROLLERS_DATA_KEY, callsign)
        return self._decode_model(raw, ControllerModel)

    async def get_controller_by_cid(self, cid: int) -> ControllerModel | None:
        callsign = await self.redis.hget(self.CONTROLLERS_CID_KEY, str(cid))
        if callsign is None:
            return None
        if isinstance(callsign, bytes):
            callsign = callsign.decode()
        return await self.get_controller_by_callsign(callsign)

    @staticmethod
    def _decode_model(raw: bytes | str | None, model):
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode()
        return model.model_validate_json(raw)
