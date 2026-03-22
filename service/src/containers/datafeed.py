from dependency_injector import containers, providers
from redis.asyncio import Redis

from gateways.vatsim.datafeed_gateway import VatsimDatafeedGateway
from repositories.redis.datafeed_repository import RedisDatafeedRepository


class DatafeedContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    redis_instance = providers.Singleton(
        Redis.from_url,
        config.redis_url,
    )

    datafeed_gateway = providers.Singleton(
        VatsimDatafeedGateway,
    )

    datafeed_repository = providers.Singleton(
        RedisDatafeedRepository,
        redis=redis_instance,
    )
