from dependency_injector import containers, providers
from pymongo import MongoClient

from repositories.mongo.api_key_repository import MongoAPIKeyRepository
from repositories.mongo.plugin_token_repository import MongoPluginTokenRepository
from repositories.mongo.user_repository import MongoUserRepository


class MongoContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    mongo_client = providers.Singleton(
        MongoClient,
        config.mongo.uri,
    )

    mongo_database = providers.Singleton(
        lambda client, name: client[name],
        mongo_client,
        name=config.mongo.database,
    )

    api_keys_collection = providers.Singleton(
        lambda db: db["api-keys"],
        mongo_database,
    )

    api_key_repository = providers.Singleton(
        MongoAPIKeyRepository,
        collection=api_keys_collection,
    )

    user_collection = providers.Singleton(
        lambda db: db["user"],
        mongo_database,
    )

    user_repository = providers.Singleton(MongoUserRepository, collection=user_collection)

    # Plugin Token

    plugin_token_collection = providers.Singleton(
        lambda db: db["plugin-token"],
        mongo_database,
    )

    plugin_token_repository = providers.Singleton(
        MongoPluginTokenRepository, collection=plugin_token_collection
    )
