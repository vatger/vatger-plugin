from dependency_injector import containers, providers

from containers.datafeed import DatafeedContainer
from containers.mongo_container import MongoContainer
from services.auth_service import AuthService
from services.plugin_token_service import PluginTokenService
from services.vatsim_service import VatsimService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    config.from_pydantic(Settings())

    mongo_container = providers.Container(MongoContainer, config=config)
    datafeed_container = providers.Container(DatafeedContainer, config=config)

    # OAuth
    vatsim_service = providers.Singleton(VatsimService)
    auth_service = providers.Singleton(
        AuthService, vatsim_service=vatsim_service, user_repo=mongo_container.user_repository
    )

    # Plugin Token
    plugin_token_service = providers.Singleton(
        PluginTokenService, repository=mongo_container.plugin_token_repository
    )
