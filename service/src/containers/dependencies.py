from dependency_injector import containers, providers

from auth.auth_service import AuthService
from auth.vatsim_auth_service import VatsimAuthService
from containers.datafeed import DatafeedContainer
from containers.mongodb_container import MongoDBContainer
from services.plugin_token_service import PluginTokenService
from services.silent_request_service import SilentRequestService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    mongo_container = providers.Container(MongoDBContainer, config=config)
    datafeed_container = providers.Container(DatafeedContainer, config=config)

    # OAuth
    vatsim_service = providers.Singleton(VatsimAuthService)
    auth_service = providers.Singleton(
        AuthService, vatsim_service=vatsim_service, user_repo=mongo_container.user_repository
    )

    # Plugin Token
    plugin_token_service = providers.Singleton(
        PluginTokenService, repository=mongo_container.plugin_token_repository
    )

    # SilentRequest
    silent_request_service = providers.Factory(
        SilentRequestService,
        repository=mongo_container.silent_request_repository,
        datafeed_repository=datafeed_container.datafeed_repository,
        allowed_airports=config.SILENT_REQUEST_ALLOWED_AIRPORTS,
    )
