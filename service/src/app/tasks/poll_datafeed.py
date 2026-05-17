import logging
from typing import TYPE_CHECKING

from app.broker import broker
from containers.dependencies import DependencyContainer

if TYPE_CHECKING:
    from models.datafeed import DatafeedModel

container = DependencyContainer()
logger = logging.getLogger(__name__)


@broker.task("poll_datafeed")
async def poll_datafeed():
    gateway = container.datafeed_container.datafeed_gateway()
    repository = container.datafeed_container.datafeed_repository()

    feed: DatafeedModel = await gateway.fetch()

    if feed is None:
        logger.warning("Feed is None, skipping update")
        return

    logger.info("Fetched feed: %d pilots, %d controllers", len(feed.pilots), len(feed.controllers))

    await repository.update(feed)
