from unittest.mock import Mock

import pytest

from models.request import SilentRequestModel
from services.request_service import RequestService


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
    req = make_request()
    repo_mock.create.return_value = req

    result = service.create_request(req)

    repo_mock.create.assert_called_once_with(req)
    assert result == req


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
