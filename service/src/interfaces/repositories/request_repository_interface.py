from abc import ABC, abstractmethod

from interfaces.repositories.base_repository import BaseRepository
from models.request import SilentRequestModel


class RequestRepositoryInterface(BaseRepository[SilentRequestModel], ABC):
    @abstractmethod
    def get_by_callsign(self, callsign: str) -> SilentRequestModel | None: ...

    @abstractmethod
    def delete_by_callsign(self, callsign: str) -> bool: ...
