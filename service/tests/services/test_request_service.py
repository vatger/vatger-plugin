from unittest.mock import Mock

import pytest

from domain.request import SilentRequestModel
from interfaces.repositories.request_repository_interface import DuplicateSilentRequestException
from services.request_service import RequestService

pytestmark = pytest.mark.unit


@pytest.fixture
def repo_mock():
    return Mock()


@pytest.fixture
def service(repo_mock):
    return RequestService(repo_mock)


def make_request(callsign="DLH123"):
    return SilentRequestModel(
        id="1",
        request_type="PUSHBACK",
        callsign=callsign,
        airport_icao="EDDF",
    )


def test_get_request_by_callsign(service, repo_mock):
    req = make_request()
    repo_mock.get_request_by_callsign.return_value = req

    result = service.get_request_by_callsign("DLH123")

    repo_mock.get_request_by_callsign.assert_called_once_with("DLH123")
    assert result == req


def test_get_request_by_callsign_not_found(service, repo_mock):
    repo_mock.get_request_by_callsign.return_value = None

    result = service.get_request_by_callsign("UNKNOWN")

    repo_mock.get_request_by_callsign.assert_called_once_with("UNKNOWN")
    assert result is None


def test_create_request(service, repo_mock):
    """test request passes no request with callsign is saved"""
    req = make_request()
    repo_mock.create.return_value = req
    repo_mock.get_request_by_callsign.return_value = None

    result = service.create_request(req)

    repo_mock.create.assert_called_once_with(req)
    assert result == req


def test_create_request_duplicate(service, repo_mock):
    """test duplicate request gets declined and returns and error"""
    req = make_request()
    repo_mock.create.return_value = req
    repo_mock.get_request_by_callsign.return_value = req

    with pytest.raises(DuplicateSilentRequestException):
        result = service.create_request(req)

        assert result is None
        repo_mock.create.assert_not_called()
        repo_mock.get_request_by_callsign.assert_not_called()


def test_delete_request_by_callsign(service, repo_mock):
    repo_mock.delete_request_by_callsign.return_value = True

    result = service.delete_request_by_callsign("DLH123")

    repo_mock.delete_request_by_callsign.assert_called_once_with("DLH123")
    assert result is True


def test_delete_request_by_callsign_not_found(service, repo_mock):
    repo_mock.delete_request_by_callsign.return_value = False

    result = service.delete_request_by_callsign("UNKNOWN")

    repo_mock.delete_request_by_callsign.assert_called_once_with("UNKNOWN")
    assert result is False


def test_get_all(service, repo_mock):
    repo_mock.get_all.return_value = [
        SilentRequestModel(
            id="1",
            request_type="PUSHBACK",
            callsign="DLH123",
            airport_icao="EDDF",
        )
    ]

    result = service.get_all_requests()

    assert isinstance(result, list)
    assert len(result) > 0
