import uuid
from abc import ABC, abstractmethod

from models.silent_request_model import SilentRequestModel


class DuplicateSilentRequestException(Exception): ...


class SilentRequestRepositoryInterface(ABC):
    @abstractmethod
    def create_request(self, request: SilentRequestModel) -> SilentRequestModel: ...

    @abstractmethod
    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None: ...

    @abstractmethod
    def get_request_by_user_id(self, id: uuid.UUID) -> SilentRequestModel | None: ...

    @abstractmethod
    def get_requests_by_icao(self, icao: str) -> list[SilentRequestModel] | None: ...

    @abstractmethod
    def get_all_requests(self) -> list[SilentRequestModel] | None: ...

    @abstractmethod
    def delete_request_by_callsign(self, callsign: str) -> bool: ...
