import uuid

import mongomock
import pytest

from models.user import User
from repositories.mongo.user_repository import MongoUserRepository, UserAlreadyExistsError

pytestmark = pytest.mark.unit


@pytest.fixture
def collection():
    client = mongomock.MongoClient()
    db = client["test_db"]
    return db["user"]


@pytest.fixture
def repo(collection):
    return MongoUserRepository(collection)


def test_add_and_get_user(repo):
    user = User(
        id=uuid.uuid4(),
        cid=1,
        name="Alice",
        rating="A",
        admin=True,
        access=True,
    )

    repo.add_user(user)

    fetched = repo.get_user_by_cid(1)

    assert fetched is not None
    assert fetched.cid == user.cid
    assert fetched.name == user.name
    assert fetched.rating == user.rating
    assert fetched.admin == user.admin
    assert fetched.access == user.access
    assert fetched.id == user.id


def test_get_user_not_found(repo):
    result = repo.get_user_by_cid(999)
    assert result is None


def test_update_user(repo):
    user = User(
        id=uuid.uuid4(),
        cid=2,
        name="Bob",
        rating="B",
    )

    repo.add_user(user)

    user.name = "Bob Updated"
    user.rating = "A"
    user.admin = True

    repo.update_user(user)

    updated = repo.get_user_by_cid(2)

    assert updated.name == "Bob Updated"
    assert updated.rating == "A"
    assert updated.admin is True


def test_update_user_not_found(repo):
    user = User(
        id=uuid.uuid4(),
        cid=3,
        name="Charlie",
        rating="C",
    )

    with pytest.raises(ValueError):
        repo.update_user(user)


def test_add_user_duplicate_cid(repo):
    user1 = User(
        id=uuid.uuid4(),
        cid=4,
        name="User1",
        rating="A",
    )

    user2 = User(
        id=uuid.uuid4(),
        cid=4,  # same cid
        name="User2",
        rating="B",
    )

    repo.add_user(user1)

    with pytest.raises(UserAlreadyExistsError):
        repo.add_user(user2)
