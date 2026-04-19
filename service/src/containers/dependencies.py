from dependency_injector import containers, providers

from containers.datafeed import DatafeedContainer
from containers.mongo_container import MongoContainer
from containers.request import RequestContainer
from services.api_key_auth_service import ApiKeyAuthService
from services.api_key_service import APIKeyService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    request_container = providers.Container(RequestContainer, config=config)
    mongo_container = providers.Container(MongoContainer, config=config)
    datafeed_container = providers.Container(DatafeedContainer, config=config)

    # Auth
    api_key_service = providers.Singleton(
        APIKeyService, repository=mongo_container.api_key_repository
    )
    auth_service = providers.Factory(
        ApiKeyAuthService,
        service=api_key_service,
    )
