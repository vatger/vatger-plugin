from dependency_injector import containers, providers
from pymongo import MongoClient

from repositories.mongo.api_key_repository import MongoAPIKeyRepository


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

    api_key_collection = providers.Singleton(
        lambda db: db["api-keys"],
        MongoAPIKeyRepository,
    )
