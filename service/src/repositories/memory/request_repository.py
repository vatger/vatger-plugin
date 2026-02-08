from collections.abc import Sequence

from interfaces.repositories.request_repository_interface import RequestRepositoryInterface
from models.request import SilentRequestModel


class MemoryRequestRepository(RequestRepositoryInterface):
    def __init__(self):
        self.requests: dict[str, SilentRequestModel] = {}

    def create(self, data: SilentRequestModel) -> SilentRequestModel:
        self.requests[data.id] = data
        return data

    def get(self, id_: str) -> SilentRequestModel | None:
        return self.requests.get(id_)

    def get_all(self) -> Sequence[SilentRequestModel]:
        return list(self.requests.values())

    def update(self, id_: str, data: SilentRequestModel) -> SilentRequestModel | None:
        if id_ not in self.requests:
            return None

        self.requests[id_] = data

        return self.requests[id_]

    def delete(self, id_: str) -> bool:
        if id_ in self.requests:
            del self.requests[id_]
            return True
        return False

    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None:
        return next(
            (req for req in self.requests.values() if req.callsign == callsign),
            None,
        )

    def delete_request_by_callsign(self, callsign: str) -> bool:
        for id_, req in list(self.requests.items()):
            if req.callsign == callsign:
                del self.requests[id_]
                return True
        return False
