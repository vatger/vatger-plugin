from taskiq import TaskiqScheduler
from taskiq_redis import RedisScheduleSource, RedisStreamBroker

from settings import Settings

settings = Settings()

broker = RedisStreamBroker(settings.redis_url)
schedule_source = RedisScheduleSource(settings.redis_url)
scheduler = TaskiqScheduler(broker=broker, sources=[schedule_source])

import app.tasks  # noqa: E402, F401
