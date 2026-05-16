import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.v1.plugin_token_controller import router
from containers.dependencies import DependencyContainer
from models.plugin_token import PluginToken
from services.plugin_token_service import UnauthorizedException

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_token():
    token = PluginToken(token="")
    token.user = "user-123"
    token.label = "test-label"
    token.last_used = "2024-01-01T00:00:00"
    return token


@pytest.fixture
def mock_plugin_token_service(mock_token):
    service = type("S", (), {})()

    def get_active_token_from_bearer(token_str: str):
        if token_str == "valid-token":
            return mock_token
        raise UnauthorizedException()

    service.get_active_token_from_bearer = get_active_token_from_bearer
    return service


@pytest.fixture
def client(mock_plugin_token_service):
    app = FastAPI()
    app.include_router(router)

    container = DependencyContainer()
    container.wire(modules=["api.v1.plugin_token_controller"])
    container.plugin_token_service.override(mock_plugin_token_service)

    with TestClient(app) as c:
        yield c

    container.reset_override()


def test_me_returns_token_info(client):
    response = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["active"] is True
    assert data["user_id"] == "user-123"
    assert data["label"] == "test-label"
    assert "last_used" in data


def test_me_missing_authorization_header_returns_401(client):
    response = client.get("/plugin-token/me")

    assert response.status_code == 401


def test_me_invalid_scheme_returns_401(client):
    response = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Basic abc123"},
    )

    assert response.status_code == 401


def test_me_empty_bearer_token_returns_401(client):
    response = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Bearer "},
    )

    assert response.status_code == 401


def test_me_invalid_token_returns_401(client):
    response = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_me_does_not_distinguish_error_types(client):
    # Both invalid inputs should behave identically
    resp1 = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Bearer invalid-1"},
    )

    resp2 = client.get(
        "/plugin-token/me",
        headers={"Authorization": "Bearer invalid-2"},
    )

    assert resp1.status_code == 401
    assert resp2.status_code == 401
