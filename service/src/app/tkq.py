from taskiq import TaskiqEvents, TaskiqState

from app.broker import broker


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_startup(state: TaskiqState) -> None:
    # await schedule_source.add_schedule(
    #     ScheduledTask(
    #         schedule_id="1",
    #         task_name=test_task.task_name,
    #         labels={},
    #         args=[],
    #         kwargs={},
    #         interval=timedelta(seconds=5),
    #     )
    # )
    pass


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def on_shutdown(state: TaskiqState) -> None:
    pass
    # await schedule_source.delete_schedule("1")
