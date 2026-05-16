import uuid

import pytest

from models.user import User
from services.plugin_token_service import (
    InvalidTokenException,
    PermissionDeniedException,
    PluginTokenService,
    TokenAlreadyAuthorizedException,
    UnauthorizedException,
)
from tests.mocks.repositories.mock_plugin_token_repository import (
    MockPluginTokenRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def repo():
    return MockPluginTokenRepository()


@pytest.fixture
def service(repo):
    return PluginTokenService(repo)


@pytest.fixture
def user1():
    return User(id=uuid.uuid4(), cid="1", name="", rating="", admin=False)


@pytest.fixture
def user2():
    return User(id=uuid.uuid4(), cid="2", name="", rating="", admin=False)


@pytest.fixture
def admin():
    return User(id=uuid.uuid4(), cid="3", name="", rating="", admin=True)


def test_get_tokens_own(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "test")

    tokens = service.get_tokens(scope="own", user=user1)

    assert len(tokens) == 1
    assert tokens[0].user == user1.id


def test_get_tokens_all_non_admin_denied(service, user1):
    with pytest.raises(PermissionDeniedException):
        service.get_tokens(scope="all", user=user1)


def test_get_tokens_all_admin(service, admin, user1):
    token1 = service.start_plugin_auth_flow()
    token2 = service.start_plugin_auth_flow()

    service.user_authorize_plugin(str(token1.id), str(user1.id), "t1")
    service.user_authorize_plugin(str(token2.id), str(admin.id), "t2")

    tokens = service.get_tokens(scope="all", user=admin)

    assert len(tokens) == 2


def test_revoke_own_token(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "test")

    service.revoke_token(str(token.id), user1)

    assert service.repo.get(token.id) is None


def test_revoke_other_users_token_denied(service, user1, user2):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user2.id), "test")

    with pytest.raises(PermissionDeniedException):
        service.revoke_token(str(token.id), user1)


def test_admin_can_revoke_any_token(service, admin, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "test")

    service.revoke_token(str(token.id), admin)

    assert service.repo.get(token.id) is None


def test_full_auth_flow(service, user1):
    token = service.start_plugin_auth_flow()

    # Not authorized yet
    result = service.exchange_polling_secret_for_token(str(token.id), token.polling_secret)
    assert result is None

    # Authorize
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    # Exchange
    result = service.exchange_polling_secret_for_token(str(token.id), token.polling_secret)

    assert result is not None


def test_wrong_secret(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    with pytest.raises(UnauthorizedException):
        service.exchange_polling_secret_for_token(str(token.id), "wrong")


def test_double_authorize(service, user1):
    token = service.start_plugin_auth_flow()

    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    with pytest.raises(TokenAlreadyAuthorizedException):
        service.user_authorize_plugin(str(token.id), str(user1.id), "label")


def test_invalid_token(service, user1):
    with pytest.raises(InvalidTokenException):
        service.revoke_token("invalid-uuid", user1)


def test_poll_after_consumption_fails(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    # First poll success
    service.exchange_polling_secret_for_token(str(token.id), token.polling_secret)

    # Second poll should fail
    with pytest.raises(InvalidTokenException):
        service.exchange_polling_secret_for_token(str(token.id), token.polling_secret)


def test_authorize_after_poll_consumed(service, user1):
    token = service.start_plugin_auth_flow()

    # simulate external mutation (poll consumed early)
    stored = service.repo.get(token.id)
    stored.polling_secret = None
    service.repo.update(stored)

    with pytest.raises(InvalidTokenException):
        service.user_authorize_plugin(str(token.id), str(user1.id), "label")


def test_redirect_invalid_when_already_authorized(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    with pytest.raises(InvalidTokenException):
        service.get_authorization_redirect(str(token.id), user1)


def test_redirect_invalid_when_no_polling_secret(service):
    token = service.start_plugin_auth_flow()

    stored = service.repo.get(token.id)
    stored.polling_secret = None
    service.repo.update(stored)

    with pytest.raises(InvalidTokenException):
        service.get_authorization_redirect(str(token.id), None)


def test_poll_never_authorized(service):
    token = service.start_plugin_auth_flow()

    result = service.exchange_polling_secret_for_token(str(token.id), token.polling_secret)

    assert result is None


def test_revoke_nonexistent_token(service, user1):
    with pytest.raises(InvalidTokenException):
        service.revoke_token(str(uuid.uuid4()), user1)


def test_get_tokens_empty(service, user1):
    tokens = service.get_tokens(scope="own", user=user1)
    assert tokens == []


def test_multiple_tokens_same_user(service, user1):
    t1 = service.start_plugin_auth_flow()
    t2 = service.start_plugin_auth_flow()

    service.user_authorize_plugin(str(t1.id), str(user1.id), "a")
    service.user_authorize_plugin(str(t2.id), str(user1.id), "b")

    tokens = service.get_tokens(scope="own", user=user1)

    assert len(tokens) == 2


def test_get_active_token_from_bearer_returns_token(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    resolved = service.get_active_token_from_bearer(token.token)

    assert resolved is not None
    assert resolved.id == token.id
    assert resolved.token == token.token
    assert resolved.user == user1.id
    assert resolved.label == "label"


def test_get_active_token_from_bearer_updates_last_used(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    before = service.repo.get(token.id)
    previous_last_used = before.last_used

    resolved = service.get_active_token_from_bearer(token.token)

    assert resolved.last_used is not None
    assert resolved.last_used >= previous_last_used

    stored = service.repo.get(token.id)
    assert stored.last_used == resolved.last_used


def test_get_active_token_from_bearer_rejects_empty_token(service):
    with pytest.raises(UnauthorizedException):
        service.get_active_token_from_bearer("")


def test_get_active_token_from_bearer_rejects_none_token(service):
    with pytest.raises(UnauthorizedException):
        service.get_active_token_from_bearer(None)  # type: ignore[arg-type]


def test_get_active_token_from_bearer_rejects_unknown_token(service):
    with pytest.raises(UnauthorizedException):
        service.get_active_token_from_bearer("does-not-exist")


def test_get_active_token_from_bearer_revoked_token_looks_unknown(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")

    service.revoke_token(str(token.id), user1)

    with pytest.raises(UnauthorizedException):
        service.get_active_token_from_bearer(token.token)


def test_get_active_token_from_bearer_invalid_and_revoked_fail_same_exception(service, user1):
    token = service.start_plugin_auth_flow()
    service.user_authorize_plugin(str(token.id), str(user1.id), "label")
    service.revoke_token(str(token.id), user1)

    with pytest.raises(UnauthorizedException) as revoked_exc:
        service.get_active_token_from_bearer(token.token)

    with pytest.raises(UnauthorizedException) as invalid_exc:
        service.get_active_token_from_bearer("invalid-token")

    assert type(revoked_exc.value) is type(invalid_exc.value)
