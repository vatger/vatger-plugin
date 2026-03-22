from datetime import timedelta

from taskiq import ScheduledTask, TaskiqEvents, TaskiqState

from app.broker import broker, schedule_source
from app.tasks.poll_datafeed import poll_datafeed
from containers.dependencies import DependencyContainer

from app.tasks import poll_datafeed

POLL_DATAFEED = "POLL_DATAFEED"

container = DependencyContainer()
container.wire(modules=[poll_datafeed])


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(state: TaskiqState) -> None:
    await schedule_source.add_schedule(
        ScheduledTask(
            schedule_id=POLL_DATAFEED,
            task_name=poll_datafeed.task_name,
            labels={},
            args=[],
            kwargs={},
            interval=timedelta(seconds=15),
        )
    )


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(state: TaskiqState) -> None:
    await schedule_source.delete_schedule(POLL_DATAFEED)
