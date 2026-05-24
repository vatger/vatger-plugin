import uuid
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.guards import get_user
from api.models.datafeed_dto import PilotDTO
from api.v1.datafeed_controller import router
from containers.dependencies import DependencyContainer
from models.datafeed import PilotModel
from models.user import User
from tests.mocks.repositories.mock_datafeed_repository import MockDatafeedRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def datafeed_repo():
    return MockDatafeedRepository()


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


@pytest.fixture
def client(datafeed_repo):
    app = FastAPI()
    app.include_router(router)

    container = DependencyContainer()
    container.wire(modules=["api.v1.datafeed_controller"])
    container.datafeed_container.datafeed_repository.override(datafeed_repo)

    def mock_get_user() -> User:
        return make_user()  # match your make_pilot default

    app.dependency_overrides[get_user] = mock_get_user

    with TestClient(app) as c:
        yield c

    container.reset_override()


def test_returns_pilot_data_for_authenticated_user(client, datafeed_repo):
    datafeed_repo.add_pilot(make_pilot(cid=1234567))

    response = client.get("/datafeed/user/pilot")

    assert response.status_code == 200
    assert response.json()["cid"] == 1234567
    assert response.json()["callsign"] == "DLH123"


def test_returns_correct_pilot_fields(client, datafeed_repo):
    datafeed_repo.add_pilot(make_pilot(cid=1234567, callsign="DLH124"))

    response = client.get("/datafeed/user/pilot")
    body = response.json()

    assert body["cid"] == 1234567
    assert body["callsign"] == "DLH124"
    assert body["altitude"] == 35000
    assert body["groundspeed"] == 450
    assert body["heading"] == 270


def test_returns_null_when_user_has_no_active_pilot(client, datafeed_repo):
    response = client.get("/datafeed/user/pilot")

    assert response.status_code == 200
    assert response.json() is None


def test_returns_null_when_different_pilot_is_online(client, datafeed_repo):
    datafeed_repo.add_pilot(make_pilot(cid=9999999))

    response = client.get("/datafeed/user/pilot")

    assert response.status_code == 200
    assert response.json() is None


def test_response_is_valid_pilot_dto(client, datafeed_repo):
    datafeed_repo.add_pilot(make_pilot(cid=1234567))

    response = client.get("/datafeed/user/pilot")

    assert response.status_code == 200
    dto = PilotDTO(**response.json())
    assert dto.cid == 1234567
