from abc import ABC, abstractmethod

from models.silent_request_model import SilentRequestModel
from models.user import User


class UserOfflineException(Exception): ...


class UserHasNoFlightplanException(Exception): ...


class UserMustBeControllerException(Exception): ...


class ExistingRequestException(Exception): ...


class NoExistingRequestException(Exception): ...


class InvalidAirportExpection(Exception): ...


class SilentRequestServiceInterface(ABC):
    @abstractmethod
    def get_requests_by_icao(self, icao: str) -> list[SilentRequestModel]: ...

    @abstractmethod
    def get_all_requests(self) -> list[SilentRequestModel]: ...

    @abstractmethod
    async def create_request(self, user: User): ...

    @abstractmethod
    async def delete_request(self, actor: User, target_callsign: str | None = None): ...
