from typing import TYPE_CHECKING

from app.broker import broker
from containers.dependencies import DependencyContainer

if TYPE_CHECKING:
    from domain.datafeed import DatafeedModel


@broker.task("poll_datafeed")
async def poll_datafeed():
    gateway = DependencyContainer().datafeed_container.datafeed_gateway()
    repository = DependencyContainer().datafeed_container.datafeed_repository()

    feed: DatafeedModel = await gateway.fetch()

    if feed is None:
        return

    await repository.update(feed)
