from dependency_injector import containers, providers

from containers.request import RequestContainer
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    request_container = providers.Container(RequestContainer, config=config)
