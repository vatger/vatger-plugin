import uuid

import mongomock
import pytest

from models.plugin_token import PluginToken
from repositories.mongo.plugin_token_repository import MongoPluginTokenRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def repo():
    client = mongomock.MongoClient()
    db = client["test_db"]
    collection = db["plugin-token"]

    return MongoPluginTokenRepository(collection)


def test_create_and_get(repo):
    token = PluginToken(
        token="abc",
        polling_secret="secret",
    )

    created = repo.create(token)

    assert created is not None
    assert created.id == token.id
    assert created.token == "abc"

    fetched = repo.get(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.token == "abc"


def test_get_nonexistent(repo):
    result = repo.get(uuid.uuid4())
    assert result is None


def test_update(repo):
    token = PluginToken(
        token="abc",
        polling_secret="secret",
    )

    created = repo.create(token)

    created.label = "updated"
    created.user = uuid.uuid4()

    updated = repo.update(created)

    assert updated is not None
    assert updated.label == "updated"
    assert updated.user == created.user

    fetched = repo.get(created.id)
    assert fetched.label == "updated"


def test_update_nonexistent(repo):
    token = PluginToken(
        id=uuid.uuid4(),
        token="abc",
        polling_secret="secret",
    )

    result = repo.update(token)
    assert result is None


def test_delete(repo):
    token = PluginToken(
        token="abc",
        polling_secret="secret",
    )

    created = repo.create(token)

    success = repo.delete(created.id)
    assert success is True

    assert repo.get(created.id) is None


def test_delete_nonexistent(repo):
    success = repo.delete(uuid.uuid4())
    assert success is False


def test_get_tokens(repo):
    t1 = repo.create(PluginToken(token="a", polling_secret="s1"))
    t2 = repo.create(PluginToken(token="b", polling_secret="s2"))

    tokens = repo.get_tokens()

    assert len(tokens) == 2
    ids = {t.id for t in tokens}

    assert t1.id in ids
    assert t2.id in ids


def test_get_tokens_by_user(repo):
    user1 = uuid.uuid4()
    user2 = uuid.uuid4()

    repo.create(PluginToken(token="a", polling_secret="s1", user=user1))
    repo.create(PluginToken(token="b", polling_secret="s2", user=user1))
    repo.create(PluginToken(token="c", polling_secret="s3", user=user2))

    tokens = repo.get_tokens_by_user(user1)

    assert len(tokens) == 2
    assert all(t.user == user1 for t in tokens)


def test_uuid_serialization(repo):
    user_id = uuid.uuid4()

    token = PluginToken(
        token="abc",
        polling_secret="secret",
        user=user_id,
    )

    created = repo.create(token)

    fetched = repo.get(created.id)

    assert isinstance(fetched.user, uuid.UUID)
    assert fetched.user == user_id
