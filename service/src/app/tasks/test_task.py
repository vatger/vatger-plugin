import logging

from app.broker import broker
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@broker.task
async def test_task():

    print(f"RUNNING at {datetime.now().isoformat()}")
