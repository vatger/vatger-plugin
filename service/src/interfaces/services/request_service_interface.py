from abc import ABC, abstractmethod

from models.request import SilentRequestModel


class RequestServiceInterface(ABC):
    @abstractmethod
    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None: ...

    @abstractmethod
    def create_request(self, request: SilentRequestModel) -> SilentRequestModel: ...

    @abstractmethod
    def delete_request_by_callsign(self, callsign: str) -> bool: ...
