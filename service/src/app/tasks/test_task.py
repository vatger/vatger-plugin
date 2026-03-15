import logging
from datetime import datetime

from app.broker import broker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@broker.task
async def test_task():
    logger.info(f"RUNNING at {datetime.now().isoformat()}")
