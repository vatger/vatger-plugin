import pytest
from fastapi.testclient import TestClient

from api.app import app, container


@pytest.fixture
def client():
    """
    Provides the FastAPI TestClient
    """

    container.reset_override()

    with TestClient(app) as client:
        yield client
