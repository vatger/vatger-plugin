import uuid
from datetime import UTC, datetime
from typing import Literal

from interfaces.repositories.datafeed_repository_interface import DatafeedRepositoryInterface
from interfaces.repositories.silent_request_repository_interface import (
    SilentRequestRepositoryInterface,
)
from interfaces.services.silent_request_service_interface import (
    ControllerOfflineException,
    ExistingRequestException,
    InvalidAirportExpection,
    NoExistingRequestException,
    SilentRequestServiceInterface,
    UserHasNoFlightplanException,
    UserMustBeControllerException,
    UserOfflineException,
)
from models.silent_request_model import SilentRequestModel
from models.user import User


class SilentRequestService(SilentRequestServiceInterface):
    def __init__(
        self,
        repository: SilentRequestRepositoryInterface,
        datafeed_repository: DatafeedRepositoryInterface,
        allowed_airports: list[str] | None = None,
    ):
        self.repo = repository
        self.datafeed_repo = datafeed_repository
        self.allowed_airports = set(allowed_airports) if allowed_airports else None

    def get_requests_by_icao(self, icao: str) -> list[SilentRequestModel]:
        return self.repo.get_requests_by_icao(icao) or []

    def get_all_requests(self) -> list[SilentRequestModel]:
        return self.repo.get_all_requests() or []

    def get_request_by_user(self, user_id: uuid.UUID) -> SilentRequestModel | None:
        return self.repo.get_request_by_user_id(user_id)

    async def create_request(self, user: User, type: Literal["TAXI", "PUSHBACK"]):
        # check if user is online as pilot
        pilot = await self.datafeed_repo.get_pilot_by_cid(int(user.cid))

        if not pilot:
            raise UserOfflineException

        if not pilot.flight_plan:
            raise UserHasNoFlightplanException

        if self.allowed_airports and pilot.flight_plan.departure not in self.allowed_airports:
            raise InvalidAirportExpection

        # check if user already has a request
        existing_req = self.repo.get_request_by_user_id(user.id)

        if existing_req and existing_req.callsign == pilot.callsign:
            if existing_req.type == type:
                raise ExistingRequestException
            else:  # request type differs, delete old request
                self.repo.delete_request_by_user(user.id)
        elif (
            existing_req and existing_req.callsign != pilot.callsign
        ):  # if there is an existing request and the callsign has changed
            self.repo.delete_request_by_user(user.id)  # delete old request

        request = SilentRequestModel(
            callsign=pilot.callsign,
            user_id=user.id,
            departure_icao=pilot.flight_plan.departure,
            type=type,
            requested_at=datetime.now(UTC),
        )

        self.repo.create_request(request)

    async def delete_request(self, actor: User, target_callsign: str | None = None):
        """If no target_callsign is provided, user requests the deletion of his own request"""

        request = None
        if target_callsign:
            request = self.repo.get_request_by_callsign(target_callsign)
        else:
            request = self.repo.get_request_by_user_id(actor.id)

        if not request:
            raise NoExistingRequestException

        if request.user_id == actor.id:
            return self.repo.delete_request_by_user(request.user_id)
        else:
            controller = await self.datafeed_repo.get_controller_by_cid(int(actor.cid))

            # admin may always delete
            if actor.admin:
                return self.repo.delete_request_by_user(request.user_id)

            # if the actor is not online as a controller and not an admin
            if not controller:
                raise ControllerOfflineException

            # deny observers
            if controller.isObserver():
                raise UserMustBeControllerException

            return self.repo.delete_request_by_user(request.user_id)
