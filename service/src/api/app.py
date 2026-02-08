from fastapi import FastAPI

from api.router import main_router
from api.v1 import silent_request_controller
from containers.dependencies import DependencyContainer

app = FastAPI()
app.include_router(main_router)

container = DependencyContainer()
container.wire(modules=[silent_request_controller])
