import pytest
from fastapi import HTTPException, status

from domain.api_key import APIKey
from services.auth_service import AuthorizationService
from tests.mocks.services.api_key_service_mock import APIKeyServiceMock

pytestmark = pytest.mark.unit


@pytest.fixture
def api_key():
    return APIKey(
        key_hash="HASHED",
        owner="TESTS",
        permissions={"permission:one", "permission:two"},
        active=True,
    )


@pytest.fixture
def key_service(api_key):
    svc = APIKeyServiceMock()
    svc.set("raw-key", api_key)
    return svc


@pytest.fixture
def auth_service(key_service):
    return AuthorizationService(key_service)


def test_authorize_returns_key_when_valid_and_has_permissions(auth_service, key_service, api_key):
    required = {"permission:one"}

    result = auth_service.authorize("raw-key", required)

    assert key_service.calls == 1
    assert key_service.last_raw_key == "raw-key"
    assert result is api_key


def test_authorize_raises_403_when_key_invalid(auth_service, key_service):
    with pytest.raises(HTTPException) as exc:
        auth_service.authorize("missing-key", {"permission:one"})

    assert key_service.calls == 1
    assert key_service.last_raw_key == "missing-key"
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Invalid API key"


def test_authorize_raises_403_when_permissions_insufficient(auth_service, key_service):
    with pytest.raises(HTTPException) as exc:
        auth_service.authorize("raw-key", {"permission:admin"})

    assert key_service.calls == 1
    assert key_service.last_raw_key == "raw-key"
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == "Insufficient permissions"


def test_authorize_allows_empty_required_set(auth_service, key_service, api_key):
    result = auth_service.authorize("raw-key", set())

    assert key_service.calls == 1
    assert result is api_key
