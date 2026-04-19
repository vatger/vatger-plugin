from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from core.security import ALGORITHM
from settings import settings

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.cid = "1234567"
    user.access = True
    user.admin = False
    return user


@pytest.fixture
def mock_user_repository(mock_user):
    repo = MagicMock()
    repo.get_user_by_cid.return_value = mock_user
    return repo


@pytest.fixture
def mock_auth_service():
    service = MagicMock()
    token = MagicMock()
    token.access = "mock_access_token"
    token.refresh = "mock_refresh_token"
    service.authenticate.return_value = token
    service.get_vatsim_connect_url.return_value = "https://auth.vatsim.net/oauth/authorize?..."
    return service


@pytest.fixture
def valid_access_token(mock_user):
    return jwt.encode(
        {"sub": mock_user.cid},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


@pytest.fixture
def valid_refresh_token(mock_user):
    return jwt.encode(
        {"sub": mock_user.cid},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


@pytest.fixture
def client(mock_user_repository, mock_auth_service):
    from api.v1.auth_controller import router
    from containers.dependencies import DependencyContainer

    app = FastAPI()
    app.include_router(router)

    container = DependencyContainer()
    container.wire(modules=["api.v1.auth_controller"])
    container.mongo_container.user_repository.override(mock_user_repository)
    container.auth_service.override(mock_auth_service)

    with TestClient(app, raise_server_exceptions=False, follow_redirects=False) as c:
        yield c

    container.reset_override()


class TestStartConnectFlow:
    def test_redirects_to_vatsim(self, client, mock_auth_service):
        response = client.get("/auth")

        assert response.status_code == 307
        assert response.headers["location"] == mock_auth_service.get_vatsim_connect_url.return_value

    def test_calls_auth_service_without_state(self, client, mock_auth_service):
        client.get("/auth")

        mock_auth_service.get_vatsim_connect_url.assert_called_once_with(None)

    def test_passes_state_to_auth_service(self, client, mock_auth_service):
        client.get("/auth?state=https://example.com/return")

        mock_auth_service.get_vatsim_connect_url.assert_called_once_with(
            "https://example.com/return"
        )


class TestVatsimConnectCallback:
    def test_sets_cookies_on_success(self, client):
        response = client.get("/auth/callback?code=valid_code")

        assert settings.COOKIE_NAME_ACCESS in response.cookies
        assert settings.COOKIE_NAME_REFRESH in response.cookies

    def test_calls_auth_service_with_code(self, client, mock_auth_service):
        client.get("/auth/callback?code=abc123")

        mock_auth_service.authenticate.assert_called_once_with("abc123")

    def test_redirects_to_root_without_state(self, client):
        response = client.get("/auth/callback?code=valid_code")

        assert response.status_code in (302, 307)
        assert response.headers["location"] == "/"

    def test_redirects_to_state_when_provided(self, client):
        response = client.get("/auth/callback?code=valid_code&state=https://example.com/return")

        assert response.status_code in (302, 307)
        assert response.headers["location"] == "https://example.com/return"

    def test_cookies_are_httponly(self, client):
        response = client.get("/auth/callback?code=valid_code")

        set_cookie_headers = response.headers.get_list("set-cookie")
        assert len(set_cookie_headers) > 0
        for header in set_cookie_headers:
            assert "HttpOnly" in header

    def test_missing_code_returns_422(self, client):
        response = client.get("/auth/callback")

        assert response.status_code == 422

    def test_auth_service_failure_returns_500(self, client, mock_auth_service):
        mock_auth_service.authenticate.side_effect = Exception("VATSIM error")
        response = client.get("/auth/callback?code=bad_code")

        assert response.status_code == 500


class TestGetUserEndpoint:
    def test_returns_user_info(self, client, valid_access_token, mock_user):
        client.cookies.set(settings.COOKIE_NAME_ACCESS, valid_access_token)
        response = client.get("/auth/user")

        assert response.status_code == 200
        data = response.json()
        assert data["cid"] == mock_user.cid
        assert data["access"] == mock_user.access
        assert data["admin"] == mock_user.admin

    def test_missing_cookie_returns_401(self, client):
        response = client.get("/auth/user")

        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client):
        client.cookies.set(settings.COOKIE_NAME_ACCESS, "not.a.valid.token")
        response = client.get("/auth/user")

        assert response.status_code == 401

    def test_token_without_sub_returns_401(self, client):
        token = jwt.encode({}, settings.SECRET_KEY, algorithm=ALGORITHM)
        client.cookies.set(settings.COOKIE_NAME_ACCESS, token)
        response = client.get("/auth/user")

        assert response.status_code == 401

    def test_user_not_in_db_returns_500(self, client, valid_access_token, mock_user_repository):
        mock_user_repository.get_user_by_cid.return_value = None
        client.cookies.set(settings.COOKIE_NAME_ACCESS, valid_access_token)
        response = client.get("/auth/user")

        assert response.status_code == 500

    def test_access_denied_returns_403(self, client, valid_access_token, mock_user):
        mock_user.access = False
        client.cookies.set(settings.COOKIE_NAME_ACCESS, valid_access_token)
        response = client.get("/auth/user")

        assert response.status_code == 403


class TestAuthRefresh:
    def test_refreshes_tokens(self, client, valid_refresh_token):
        client.cookies.set(settings.COOKIE_NAME_REFRESH, valid_refresh_token)
        response = client.post("/auth/refresh")

        assert response.status_code == 200
        assert settings.COOKIE_NAME_ACCESS in response.cookies
        assert settings.COOKIE_NAME_REFRESH in response.cookies

    def test_new_tokens_differ_from_old(self, client, valid_refresh_token):
        client.cookies.set(settings.COOKIE_NAME_REFRESH, valid_refresh_token)
        response = client.post("/auth/refresh")

        new_access = response.cookies.get(settings.COOKIE_NAME_ACCESS)
        assert new_access != valid_refresh_token

    def test_missing_refresh_cookie_returns_401(self, client):
        response = client.post("/auth/refresh")

        assert response.status_code == 401

    def test_invalid_refresh_token_returns_401(self, client):
        client.cookies.set(settings.COOKIE_NAME_REFRESH, "invalid.token.here")
        response = client.post("/auth/refresh")

        assert response.status_code == 401

    def test_token_without_sub_returns_401(self, client):
        token = jwt.encode({}, settings.SECRET_KEY, algorithm=ALGORITHM)
        client.cookies.set(settings.COOKIE_NAME_REFRESH, token)
        response = client.post("/auth/refresh")

        assert response.status_code == 401
