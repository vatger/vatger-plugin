from dependency_injector import containers, providers

from repositories.memory.request_repository import MemoryRequestRepository
from services.request_service import RequestService


class RequestContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    request_repository = providers.Singleton(MemoryRequestRepository)

    request_service = providers.Singleton(RequestService, request_repository)
