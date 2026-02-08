from models.request import SilentRequestModel
from repositories.memory.request_repository import MemoryRequestRepository


def make_request(
    callsign="DLH123",
):
    return SilentRequestModel(
        id=callsign,
        request_type="PUSHBACK",
        callsign=callsign,
        airport_icao="EDDF",
    )


def test_create_and_get():
    repo = MemoryRequestRepository()
    req = make_request()

    repo.create(req)
    result = repo.get(req.id)

    assert result is not None
    assert result.id == req.id
    assert result.callsign == "DLH123"


def test_get_returns_none_when_missing():
    repo = MemoryRequestRepository()
    assert repo.get("missing") is None


def test_get_all_returns_all_requests():
    repo = MemoryRequestRepository()
    r1 = make_request("DLH123")
    r2 = make_request("DLH456")

    repo.create(r1)
    repo.create(r2)

    all_requests = repo.get_all()

    assert len(all_requests) == 2
    ids = {r.id for r in all_requests}
    assert ids == {"DLH123", "DLH456"}


def test_update_existing():
    repo = MemoryRequestRepository()
    req = make_request("DLH123")
    repo.create(req)

    updated = SilentRequestModel(
        id="DLH123",
        request_type="TAXI",
        callsign="DLH123",
        airport_icao="EDDF",
    )

    result = repo.update("DLH123", updated)

    assert result is not None
    assert result.request_type == "TAXI"
    assert repo.get("DLH123").request_type == "TAXI"


def test_update_missing_returns_none():
    repo = MemoryRequestRepository()
    req = make_request("DLH999")

    assert repo.update("DLH999", req) is None


def test_delete_existing():
    repo = MemoryRequestRepository()
    req = make_request("DLH123")
    repo.create(req)

    deleted = repo.delete("DLH123")

    assert deleted is True
    assert repo.get("DLH123") is None


def test_delete_missing():
    repo = MemoryRequestRepository()
    assert repo.delete("missing") is False


def test_get_by_callsign_found():
    repo = MemoryRequestRepository()
    req = make_request("DLH123")
    repo.create(req)

    result = repo.get_by_callsign("DLH123")

    assert result is not None
    assert result.id == "DLH123"


def test_get_by_callsign_not_found():
    repo = MemoryRequestRepository()
    assert repo.get_by_callsign("UNKNOWN") is None


def test_delete_by_callsign_found():
    repo = MemoryRequestRepository()
    req = make_request("DLH123")
    repo.create(req)

    deleted = repo.delete_by_callsign("DLH123")

    assert deleted is True
    assert repo.get("DLH123") is None


def test_delete_by_callsign_not_found():
    repo = MemoryRequestRepository()

    deleted = repo.delete_by_callsign("UNKNOWN")

    assert deleted is False
