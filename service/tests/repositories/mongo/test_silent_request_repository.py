import uuid
from datetime import UTC, datetime

import mongomock
import pytest

from interfaces.repositories.silent_request_repository_interface import (
    DuplicateSilentRequestException,
)
from models.silent_request_model import SilentRequestModel
from repositories.mongo.silent_request_repository import MongoSilentRequestRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def repo():
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["silent-requests"]

    return MongoSilentRequestRepository(collection)


@pytest.fixture
def sample_request():
    return SilentRequestModel(
        callsign="DLH123",
        user_id=uuid.uuid4(),
        departure_icao="EDDF",
        requested_at=datetime.now(UTC),
    )


def test_create_and_get_by_callsign(repo, sample_request):
    created = repo.create_request(sample_request)

    assert created is not None
    assert created.callsign == sample_request.callsign
    assert created.user_id == sample_request.user_id
    assert created.departure_icao == sample_request.departure_icao

    fetched = repo.get_request_by_callsign(sample_request.callsign)

    assert fetched is not None
    assert fetched.callsign == sample_request.callsign
    assert fetched.user_id == sample_request.user_id


def test_get_by_callsign_nonexistent(repo):
    result = repo.get_request_by_callsign("NONE99")
    assert result is None


def test_create_and_get_by_user_id(repo, sample_request):
    repo.create_request(sample_request)

    fetched = repo.get_request_by_user_id(sample_request.user_id)

    assert fetched is not None
    assert fetched.user_id == sample_request.user_id
    assert fetched.callsign == sample_request.callsign


def test_get_by_user_id_nonexistent(repo):
    result = repo.get_request_by_user_id(uuid.uuid4())
    assert result is None


def test_create_duplicate_callsign_raises(repo, sample_request):
    repo.create_request(sample_request)

    duplicate = SilentRequestModel(
        callsign=sample_request.callsign,
        user_id=uuid.uuid4(),
        departure_icao="EDDF",
        requested_at=datetime.now(UTC),
    )

    with pytest.raises(DuplicateSilentRequestException):
        repo.create_request(duplicate)


def test_create_duplicate_user_id_raises(repo, sample_request):
    repo.create_request(sample_request)

    duplicate = SilentRequestModel(
        callsign="EWG123",
        user_id=sample_request.user_id,
        departure_icao="EDDF",
        requested_at=datetime.now(UTC),
    )

    with pytest.raises(DuplicateSilentRequestException):
        repo.create_request(duplicate)


def test_get_requests_by_icao(repo):
    user1, user2, user3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()

    repo.create_request(
        SilentRequestModel(
            callsign="DLH1", user_id=user1, departure_icao="EDDF", requested_at=datetime.now(UTC)
        )
    )
    repo.create_request(
        SilentRequestModel(
            callsign="DLH2", user_id=user2, departure_icao="EDDF", requested_at=datetime.now(UTC)
        )
    )
    repo.create_request(
        SilentRequestModel(
            callsign="DLH3", user_id=user3, departure_icao="EDDM", requested_at=datetime.now(UTC)
        )
    )

    results = repo.get_requests_by_icao("EDDF")

    assert len(results) == 2
    assert all(r.departure_icao == "EDDF" for r in results)


def test_get_requests_by_icao_nonexistent(repo, sample_request):
    repo.create_request(sample_request)

    results = repo.get_requests_by_icao("ZZZZ")

    assert results is None or results == []


def test_get_all_requests(repo):
    user1, user2 = uuid.uuid4(), uuid.uuid4()

    r1 = repo.create_request(
        SilentRequestModel(
            callsign="DLH1", user_id=user1, departure_icao="EDDF", requested_at=datetime.now(UTC)
        )
    )
    r2 = repo.create_request(
        SilentRequestModel(
            callsign="DLH3", user_id=user2, departure_icao="EDDF", requested_at=datetime.now(UTC)
        )
    )

    results = repo.get_all_requests()

    assert len(results) == 2
    callsigns = {r.callsign for r in results}
    assert r1.callsign in callsigns
    assert r2.callsign in callsigns


def test_get_all_requests_empty(repo):
    results = repo.get_all_requests()
    assert results is None or results == []


def test_delete_request_by_callsign(repo, sample_request):
    repo.create_request(sample_request)

    success = repo.delete_request_by_callsign(sample_request.callsign)
    assert success is True

    assert repo.get_request_by_callsign(sample_request.callsign) is None


def test_delete_request_nonexistent(repo):
    success = repo.delete_request_by_callsign("NONE99")
    assert success is False


def test_uuid_serialization(repo):
    user_id = uuid.uuid4()

    request = SilentRequestModel(
        callsign="DLH123",
        user_id=user_id,
        departure_icao="EDDF",
        requested_at=datetime.now(UTC),
    )

    repo.create_request(request)

    fetched = repo.get_request_by_callsign("DLH123")

    assert isinstance(fetched.user_id, uuid.UUID)
    assert fetched.user_id == user_id


def test_datetime_serialization(repo):
    requested_at = datetime(2024, 6, 1, 12, 0, 0, tzinfo=UTC)

    request = SilentRequestModel(
        callsign="DLH123",
        user_id=uuid.uuid4(),
        departure_icao="EDDF",
        requested_at=requested_at,
    )

    repo.create_request(request)

    fetched = repo.get_request_by_callsign("DLH123")

    assert isinstance(fetched.requested_at, datetime)
    assert fetched.requested_at == requested_at
