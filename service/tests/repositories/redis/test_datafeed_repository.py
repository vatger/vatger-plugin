from datetime import UTC, datetime

import fakeredis
import pytest

from domain.datafeed import DatafeedModel, PilotModel
from repositories.redis.datafeed_repository import RedisDatafeedRepository


@pytest.fixture
def redis_client():
    client = fakeredis.aioredis.FakeRedis()
    yield client


@pytest.fixture
def repository(redis_client):
    return RedisDatafeedRepository(redis_client)


def make_pilot(**overrides) -> PilotModel:
    now = datetime.now(UTC)

    data = {
        "callsign": "TEST123",
        "latitude": 51.0,
        "longitude": 8.0,
        "altitude": 30000,
        "groundspeed": 450,
        "heading": 180,
        "qnh_i_hg": 29.92,
        "qnh_mb": 1013,
        "flight_plan": None,
        "logon_time": now,
        "last_updated": now,
    }

    data.update(overrides)
    return PilotModel.model_validate(data)


def make_feed(pilots: list[PilotModel]) -> DatafeedModel:
    return DatafeedModel.model_validate({
        "pilots": pilots,
        "controllers": [],
    })


@pytest.mark.asyncio
async def test_update_stores_callsigns(repository):
    feed = make_feed([
        make_pilot(callsign="ABC123"),
        make_pilot(callsign="XYZ789"),
    ])

    await repository.update(feed)

    assert await repository.has_callsign("ABC123") is True
    assert await repository.has_callsign("XYZ789") is True
    assert await repository.has_callsign("NON_EXISTING") is False


@pytest.mark.asyncio
async def test_get_pilot_data_returns_model(repository):
    feed = make_feed([
        make_pilot(callsign="ABC123", latitude=50.0, longitude=8.0),
    ])

    await repository.update(feed)

    pilot = await repository.get_pilot_data("ABC123")

    assert isinstance(pilot, PilotModel)
    assert pilot.callsign == "ABC123"
    assert pilot.latitude == 50.0
    assert pilot.longitude == 8.0


@pytest.mark.asyncio
async def test_get_pilot_data_missing_returns_none(repository):
    feed = make_feed([])

    await repository.update(feed)

    result = await repository.get_pilot_data("MISSING")

    assert result is None


@pytest.mark.asyncio
async def test_update_removes_old_callsigns(repository):
    feed1 = make_feed([
        make_pilot(callsign="OLD1"),
        make_pilot(callsign="OLD2"),
    ])

    feed2 = make_feed([
        make_pilot(callsign="NEW1"),
    ])

    await repository.update(feed1)
    await repository.update(feed2)

    assert await repository.has_callsign("OLD1") is False
    assert await repository.has_callsign("OLD2") is False
    assert await repository.has_callsign("NEW1") is True


@pytest.mark.asyncio
async def test_old_pilot_data_removed(repository):
    feed1 = make_feed([
        make_pilot(callsign="OLD1"),
    ])

    feed2 = make_feed([])

    await repository.update(feed1)
    await repository.update(feed2)

    pilot = await repository.get_pilot_data("OLD1")

    assert pilot is None
