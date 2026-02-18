from interfaces.repositories.request_repository_interface import RequestRepositoryInterface
from interfaces.services.request_service_interface import RequestServiceInterface
from models.request import SilentRequestModel


class RequestService(RequestServiceInterface):
    def __init__(self, repository: RequestRepositoryInterface):
        self.repo = repository

    def get_all_requests(self):
        return list(self.repo.get_all())

    def get_request_by_callsign(self, callsign: str) -> SilentRequestModel | None:
        return self.repo.get_request_by_callsign(callsign)

    def create_request(self, request: SilentRequestModel) -> SilentRequestModel:
        return self.repo.create(request)

    def delete_request_by_callsign(self, callsign: str) -> bool:
        return self.repo.delete_request_by_callsign(callsign)
