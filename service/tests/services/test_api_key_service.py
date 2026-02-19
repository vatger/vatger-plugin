import pytest

from models.api_key import APIKey
from services.api_key_service import APIKeyService
from tests.mocks.repositories.api_key_repository_mock import APIKeyRepositoryMock

pytestmark = pytest.mark.unit


@pytest.fixture
def repository():
    initial = [
        APIKey(key_hash="HASHED", owner="TESTS", permissions={"permission:one"}, active=True)
    ]

    return APIKeyRepositoryMock(initial)


@pytest.fixture
def service(repository):
    return APIKeyService(repository, hasher=lambda _: "HASHED")


def test_validate_key_uses_hash_and_calls_repo(repository, service):
    key = service.validate_key("raw-key")

    assert repository.calls == 1
    assert repository.last_hash == "HASHED"
    assert key is not None
    assert key.key_hash == "HASHED"


def test_validate_key_returns_none_when_key_not_found():
    repo = APIKeyRepositoryMock(initial=[])
    service = APIKeyService(repo, hasher=lambda _: "MISSING")

    assert service.validate_key("raw-key") is None
    assert repo.calls == 1
    assert repo.last_hash == "MISSING"


def test_validate_key_calls_repo_every_time(repository, service):
    assert service.validate_key("k1") is not None
    assert service.validate_key("k2") is not None
    assert repository.calls == 2


def test_validate_key_uses_hasher_output_to_find_key():
    # repo contains key_hash="EXPECTED"
    repo = APIKeyRepositoryMock(
        initial=[APIKey(key_hash="EXPECTED", owner="TESTS", permissions={"p"}, active=True)]
    )

    service = APIKeyService(repo, hasher=lambda _: "EXPECTED")
    key = service.validate_key("raw-key")

    assert key is not None
    assert key.key_hash == "EXPECTED"
    assert repo.last_hash == "EXPECTED"
