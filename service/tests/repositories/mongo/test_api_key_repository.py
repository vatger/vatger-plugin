import mongomock
import pytest

from models.api_key import APIKey
from repositories.mongo.api_key_repository import MongoAPIKeyRepository


@pytest.fixture
def collection():
    client = mongomock.MongoClient()
    db = client["test_db"]
    return db["api_keys"]


@pytest.fixture
def repo(collection):
    return MongoAPIKeyRepository(collection)


def test_get_by_hash_returns_none_when_not_found(repo):
    assert repo.get_by_hash("missing-hash") is None


def test_get_by_hash_returns_domain_object_when_found(repo, collection):
    collection.insert_one({
        "key_hash": "abc123",
        "owner": "leon",
        "permissions": ["read", "write"],
        "active": True,
    })

    api_key = repo.get_by_hash("abc123")

    assert api_key == APIKey(
        key_hash="abc123",
        owner="leon",
        permissions={"read", "write"},
        active=True,
    )


def test_to_domain_handles_missing_permissions_as_empty_set(repo, collection):
    collection.insert_one({
        "key_hash": "no-perms",
        "owner": "leon",
        # no "permissions"
        "active": True,
    })

    api_key = repo.get_by_hash("no-perms")

    assert api_key is not None
    assert api_key.permissions == set()


def test_to_domain_defaults_active_to_true_when_missing(repo, collection):
    collection.insert_one({
        "key_hash": "default-active",
        "owner": "leon",
        "permissions": ["read"],
        # no "active"
    })

    api_key = repo.get_by_hash("default-active")

    assert api_key is not None
    assert api_key.active is True


def test_permissions_are_deduplicated(repo, collection):
    collection.insert_one({
        "key_hash": "dupes",
        "owner": "leon",
        "permissions": ["read", "read", "write"],
        "active": True,
    })

    api_key = repo.get_by_hash("dupes")

    assert api_key is not None
    assert api_key.permissions == {"read", "write"}
