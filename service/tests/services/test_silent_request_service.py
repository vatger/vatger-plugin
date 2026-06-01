import uuid
from datetime import UTC, datetime

import pytest

from interfaces.services.silent_request_service_interface import (
    ControllerOfflineException,
    ExistingRequestException,
    InvalidAirportExpection,
    NoExistingRequestException,
    UserHasNoFlightplanException,
    UserMustBeControllerException,
    UserOfflineException,
)
from models.datafeed import ControllerModel, PilotModel
from models.silent_request_model import SilentRequestModel
from models.user import User
from services.silent_request_service import SilentRequestService
from tests.mocks.repositories.mock_datafeed_repository import MockDatafeedRepository
from tests.mocks.repositories.mock_silent_request_repository import MockSilentRequestRepository

pytestmark = pytest.mark.unit


def make_user(cid: int = 1234567, user_id: uuid.UUID | None = None) -> User:
    if not user_id:
        user_id = uuid.uuid4()

    return User(
        id=user_id,
        cid=cid,
        name="",
        rating="S2",
        access=True,
    )


def make_flight_plan(**overrides) -> PilotModel.FlightPlanModel:
    defaults = {
        "flight_rules": "I",
        "aircraft": "B738",
        "aircraft_faa": "B738/L",
        "departure": "EDDF",
        "arrival": "EGLL",
        "alternate": "EGLC",
        "deptime": "",
        "enroute_time": "",
        "fuel_time": "",
        "remarks": "",
        "route": "",
        "revision_id": 1,
    }
    defaults.update(overrides)
    return PilotModel.FlightPlanModel(**defaults)


def make_pilot(cid: int = 1234567, callsign: str = "DLH123", flight_plan=True) -> PilotModel:
    return PilotModel(
        cid=cid,
        callsign=callsign,
        latitude=50.0,
        longitude=8.0,
        altitude=35000,
        groundspeed=450,
        heading=270,
        qnh_i_hg=29.92,
        qnh_mb=1013,
        flight_plan=make_flight_plan() if flight_plan else None,
        logon_time=datetime.now(UTC),
        last_updated=datetime.now(UTC),
    )


def make_controller(cid: int, facility: int = 1) -> ControllerModel:
    return ControllerModel(
        cid=cid,
        name="",
        callsign="EDDF_DEL",
        facility=facility,
        frequency="125.250",
        rating=3,
        server="",
        visual_range=50,
        logon_time=datetime.now(UTC),
        last_updated=datetime.now(UTC),
    )


@pytest.fixture
def datafeed_repo():
    return MockDatafeedRepository()


@pytest.fixture
def silent_repo():
    return MockSilentRequestRepository()


@pytest.fixture
def service(silent_repo, datafeed_repo):
    return SilentRequestService(
        repository=silent_repo,
        datafeed_repository=datafeed_repo,
    )


@pytest.mark.asyncio
async def test_create_request_raises_when_user_offline(service):
    user = make_user(cid=9999999)
    # user is offline
    with pytest.raises(UserOfflineException):
        await service.create_request(user, type="TAXI")


@pytest.mark.asyncio
async def test_create_request_raises_when_no_flight_plan(service, datafeed_repo):
    pilot = make_pilot(flight_plan=False)

    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)
    with pytest.raises(UserHasNoFlightplanException):
        await service.create_request(user, type="TAXI")


@pytest.mark.asyncio
async def test_create_request_raises_when_identical_request_exists(
    service, datafeed_repo, silent_repo
):
    pilot = make_pilot()
    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)
    # create an existing request with the same callsign
    existing = SilentRequestModel(
        callsign=pilot.callsign,
        user_id=user.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(existing)

    with pytest.raises(ExistingRequestException):
        await service.create_request(user, type="TAXI")


@pytest.mark.asyncio
async def test_create_request_replaces_request_when_callsign_changed(
    service, datafeed_repo, silent_repo
):
    new_callsign = "DLH456"
    pilot = make_pilot(callsign=new_callsign)
    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)
    # create an existing request with a different callsign
    old_callsign = "DLH123"
    old_request = SilentRequestModel(
        callsign=old_callsign,
        user_id=user.id,
        departure_icao="EDDM",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(old_request)

    await service.create_request(user, type="TAXI")

    # old callsign must be gone
    remaining = silent_repo.get_all_requests()
    callsigns = [r.callsign for r in remaining]
    assert old_callsign not in callsigns

    # new request must exist with updated callsign
    new_req = silent_repo.get_request_by_user_id(user.id)
    assert new_req is not None
    assert new_req.callsign == new_callsign


@pytest.mark.asyncio
async def test_create_request_happy_path(service, datafeed_repo, silent_repo):
    pilot = make_pilot()
    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)
    await service.create_request(user, type="TAXI")

    req = silent_repo.get_request_by_user_id(user.id)
    assert req is not None
    assert req.callsign == pilot.callsign
    assert req.departure_icao == pilot.flight_plan.departure
    assert req.user_id == user.id
    assert req.requested_at is not None


@pytest.mark.asyncio
async def test_create_request_upgrade(service, datafeed_repo, silent_repo):
    pilot = make_pilot()
    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)
    await service.create_request(user, type="PUSHBACK")

    req = silent_repo.get_request_by_user_id(user.id)
    assert req is not None
    assert req.callsign == pilot.callsign
    assert req.departure_icao == pilot.flight_plan.departure
    assert req.type == "PUSHBACK"
    assert req.user_id == user.id
    assert req.requested_at is not None

    # upgrade request to TAXI
    await service.create_request(user, type="TAXI")

    req = silent_repo.get_request_by_user_id(user.id)
    assert req is not None
    assert req.callsign == pilot.callsign
    assert req.departure_icao == pilot.flight_plan.departure
    assert req.type == "TAXI"
    assert req.user_id == user.id
    assert req.requested_at is not None


@pytest.mark.asyncio
async def test_invalid_airport(service, datafeed_repo, silent_repo):
    allowed_airports = ["EDDM"]
    service = SilentRequestService(
        repository=silent_repo, datafeed_repository=datafeed_repo, allowed_airports=allowed_airports
    )

    pilot = make_pilot()
    pilot.flight_plan.departure = "EDDF"  # set departure again to assert test setup is correct
    datafeed_repo.add_pilot(pilot)

    user = make_user(cid=pilot.cid)

    with pytest.raises(InvalidAirportExpection):
        await service.create_request(user, type="TAXI")


def test_get_requests_by_user_returns_matching_requests(service, silent_repo):
    r1 = SilentRequestModel(
        callsign="DLH1",
        user_id=uuid.uuid4(),
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    r2 = SilentRequestModel(
        callsign="BAW1",
        user_id=uuid.uuid4(),
        departure_icao="EGLL",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(r1)
    silent_repo.create_request(r2)

    result = service.get_request_by_user(r1.user_id)

    assert result.callsign == "DLH1"

    result = service.get_request_by_user(r2.user_id)
    assert result.callsign == "BAW1"


def test_get_requests_by_icao_returns_matching_requests(service, silent_repo):
    r1 = SilentRequestModel(
        callsign="DLH1",
        user_id=uuid.uuid4(),
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    r2 = SilentRequestModel(
        callsign="BAW1",
        user_id=uuid.uuid4(),
        departure_icao="EGLL",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(r1)
    silent_repo.create_request(r2)

    result = service.get_requests_by_icao("EDDF")
    assert len(result) == 1
    assert result[0].callsign == "DLH1"


def test_get_requests_by_icao_returns_empty_when_no_match(service):
    result = service.get_requests_by_icao("ZZZZ")
    assert result == []


def test_get_all_requests_returns_empty_list_when_no_requests(service):
    result = service.get_all_requests()
    assert result == []


@pytest.mark.asyncio
async def test_delete_own_request_raises_when_no_request_exists(service):
    user = make_user()
    with pytest.raises(NoExistingRequestException):
        await service.delete_request(actor=user)


@pytest.mark.asyncio
async def test_delete_own_request_removes_the_request(service, silent_repo):
    user = make_user()
    request = SilentRequestModel(
        callsign="DLH1",
        user_id=user.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(request)

    await service.delete_request(actor=user)

    assert silent_repo.get_request_by_user_id(user.id) is None


@pytest.mark.asyncio
async def test_delete_own_request_does_not_affect_other_users_requests(service, silent_repo):
    user = make_user(cid=1111111)
    other_user = make_user(cid=2222222)

    r1 = SilentRequestModel(
        callsign="DLH1",
        user_id=user.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )

    r2 = SilentRequestModel(
        callsign="DLH2",
        user_id=other_user.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )

    silent_repo.create_request(r1)
    silent_repo.create_request(r2)

    await service.delete_request(actor=user)

    assert silent_repo.get_request_by_user_id(other_user.id) is not None


@pytest.mark.asyncio
async def test_delete_by_callsign_raises_when_callsign_not_found(service):
    actor = make_user()
    with pytest.raises(NoExistingRequestException):
        await service.delete_request(actor=actor, target_callsign="UNKNOWN")


@pytest.mark.asyncio
async def test_delete_by_callsign_own_callsign_succeeds(service, silent_repo):
    user = make_user()
    request = SilentRequestModel(
        callsign="DLH123",
        user_id=user.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(request)

    await service.delete_request(actor=user, target_callsign=request.callsign)

    assert silent_repo.get_request_by_user_id(user.id) is None


@pytest.mark.asyncio
async def test_delete_other_users_request_raises_when_actor_offline(
    service, silent_repo, datafeed_repo
):
    """Actor is not online as a controller"""
    pilot = make_user(cid=1111111)
    actor = make_user(cid=9999999)  # not in datafeed

    request = SilentRequestModel(
        callsign="DLH123",
        user_id=pilot.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(request)

    # datafeed has no controller for actor.cid, therefor
    with pytest.raises(ControllerOfflineException):
        await service.delete_request(actor=actor, target_callsign="DLH123")


@pytest.mark.asyncio
async def test_delete_other_users_request_raises_when_actor_is_observer(
    service, silent_repo, datafeed_repo
):
    """Actor is online but has facility=0 (observer) — UserMustBeControllerException expected."""
    owner = make_user(cid=1111111)
    actor = make_user(cid=2222222)

    request = SilentRequestModel(
        callsign="DLH123",
        user_id=owner.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(request)

    datafeed_repo.add_controller(make_controller(actor.cid, facility=0))

    with pytest.raises(UserMustBeControllerException):
        await service.delete_request(actor=actor, target_callsign="DLH123")


@pytest.mark.asyncio
async def test_delete_other_users_request_succeeds_when_actor_is_controller(
    service, silent_repo, datafeed_repo
):
    """Actor is online but has facility=0 (observer) — UserMustBeControllerException expected."""
    owner = make_user(cid=1111111)
    actor = make_user(cid=2222222)

    request = SilentRequestModel(
        callsign="DLH123",
        user_id=owner.id,
        departure_icao="EDDF",
        type="TAXI",
        requested_at=datetime.now(UTC),
    )
    silent_repo.create_request(request)

    datafeed_repo.add_controller(make_controller(actor.cid, facility=1))

    await service.delete_request(actor=actor, target_callsign="DLH123")

    assert silent_repo.get_request_by_user_id(owner.id) is None
