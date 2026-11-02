import os
import time

import jwt
import pytest

from clients.api_client import ApiClient
from utils.config import USERS

pytestmark = [pytest.mark.api]


@pytest.mark.smoke
def test_health_endpoint_is_public(anonymous_api: ApiClient):
    response = anonymous_api.health()
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.smoke
@pytest.mark.parametrize("role", ["admin", "agent", "reporter"])
def test_login_returns_token_and_user(anonymous_api: ApiClient, role: str):
    username, password = USERS[role]
    response = anonymous_api.login(username, password)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2, "JWT has three dot separated parts"
    assert body["user"] == {"id": body["user"]["id"], "username": username, "role": role}


@pytest.mark.parametrize(
    "username, password",
    [
        ("admin", "wrong-password"),
        ("no-such-user", "Admin123!"),
        ("", ""),
    ],
    ids=["wrong-password", "unknown-user", "empty-fields"],
)
def test_login_rejects_invalid_credentials(anonymous_api: ApiClient, username: str, password: str):
    response = anonymous_api.login(username, password)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    assert anonymous_api.token is None


def test_me_requires_authentication(anonymous_api: ApiClient):
    response = anonymous_api.me()
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_me_rejects_tampered_token(anonymous_api: ApiClient, admin_api: ApiClient):
    anonymous_api.token = admin_api.token[:-3] + "abc"
    response = anonymous_api.me()
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_me_returns_current_user(agent_api: ApiClient):
    response = agent_api.me()
    assert response.status_code == 200
    assert response.json()["username"] == "agent"
    assert response.json()["role"] == "agent"


def test_admin_authentication_with_an_expired_token(anonymous_api: ApiClient):
    payload = {
    "sub": "admin",
    "role": "admin",
    "exp": time.time() - 3600
    }
    secret = os.getenv("TICKETDESK_SECRET", "change-me-in-real-environments")
    expired_create_token = jwt.encode(payload, secret, algorithm="HS256")
    anonymous_api.token = expired_create_token
    response = anonymous_api.me()
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"

    
def test_me_rejects_malformed_authorization_header(anonymous_api: ApiClient):
    response = anonymous_api._request(
        "GET", 
        "/api/users/me", 
        headers={"Authorization": "NotBearer"} 
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"