from typing import Callable, Dict

import pytest
from fastapi.testclient import TestClient

from ledgerly import auth, models
from ledgerly.main import app


@pytest.fixture(autouse=True)
def _reset_state():
    models.store.reset()
    models.seed(models.store)
    auth._clear_tokens()
    yield


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["token"]


@pytest.fixture()
def user_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        json={"username": "alice", "password": "alice123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["token"]


@pytest.fixture()
def bob_token(client: TestClient) -> str:
    response = client.post(
        "/auth/login",
        json={"username": "bob", "password": "bob123"},
    )
    assert response.status_code == 200, response.text
    return response.json()["token"]


@pytest.fixture()
def auth_header() -> Callable[[str], Dict[str, str]]:
    def _make(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return _make
