from dependency_injector import containers, providers

from containers.datafeed import DatafeedContainer
from containers.mongo_container import MongoContainer
from containers.request import RequestContainer
from services.api_key_auth_service import ApiKeyAuthService
from services.api_key_service import APIKeyService
from services.auth_service import AuthService
from services.plugin_token_service import PluginTokenService
from services.vatsim_service import VatsimService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    request_container = providers.Container(RequestContainer, config=config)
    mongo_container = providers.Container(MongoContainer, config=config)
    datafeed_container = providers.Container(DatafeedContainer, config=config)

    # API Key Auth
    api_key_service = providers.Singleton(
        APIKeyService, repository=mongo_container.api_key_repository
    )
    api_key_auth_service = providers.Factory(
        ApiKeyAuthService,
        service=api_key_service,
    )

    # OAuth
    vatsim_service = providers.Singleton(VatsimService)
    auth_service = providers.Singleton(
        AuthService, vatsim_service=vatsim_service, user_repo=mongo_container.user_repository
    )

    # Plugin Token
    plugin_token_service = providers.Singleton(
        PluginTokenService, repository=mongo_container.plugin_token_repository
    )
