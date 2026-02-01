from fastapi import FastAPI

from api.router import main_router
from containers.dependencies import DependencyContainer

app = FastAPI()
app.include_router(main_router)

container = DependencyContainer()
container.wire(modules=[])
