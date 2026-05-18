import uuid

from interfaces.repositories.silent_request_repository_interface import (
    DuplicateSilentRequestException,
    SilentRequestRepositoryInterface,
)
from models.silent_request_model import SilentRequestModel


class MockSilentRequestRepository(SilentRequestRepositoryInterface):
    def __init__(self):
        self._requests: dict[uuid.UUID, SilentRequestModel] = {}

    def create_request(self, request: SilentRequestModel) -> SilentRequestModel:
        if any(r.callsign == request.callsign for r in self._requests.values()):
            msg = f"Request with callsign '{request.callsign}' already exists"
            raise DuplicateSilentRequestException(msg)
        self._requests[request.user_id] = request
        return request

    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None:
        return next((r for r in self._requests.values() if r.callsign == callsign), None)

    def get_request_by_user_id(self, id: uuid.UUID) -> SilentRequestModel | None:
        return self._requests.get(id)

    def get_requests_by_icao(self, icao: str) -> list[SilentRequestModel] | None:
        results = [r for r in self._requests.values() if r.departure_icao == icao]
        return results or None

    def get_all_requests(self) -> list[SilentRequestModel] | None:
        requests = list(self._requests.values())
        return requests or None

    def delete_request_by_callsign(self, callsign: str) -> bool:
        for user_id, request in self._requests.items():
            if request.callsign == callsign:
                del self._requests[user_id]
                return True
        return False
