from dependency_injector import containers, providers

from containers.mongo_container import MongoContainer
from containers.request import RequestContainer
from services.api_key_service import APIKeyService
from services.auth_service import AuthorizationService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    request_container = providers.Container(RequestContainer, config=config)
    mongo_container = providers.Container(MongoContainer, config=config)

    # Auth
    api_key_service = providers.Singleton(
        APIKeyService, repository=mongo_container.api_key_repository
    )
    auth_service = providers.Factory(
        AuthorizationService,
        service=api_key_service,
    )
