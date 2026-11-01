import logging

import requests

from utils.config import USERS, settings

log = logging.getLogger("ticketdesk.api")


class ApiClient:
    """Thin wrapper around the TicketDesk REST API.

    Every method returns the raw Response so tests decide what to assert.
    A session object with a requests-like interface can be injected for
    in-process testing (for example FastAPI's TestClient).
    """

    def __init__(self, base_url: str | None = None, session=None):
        self.base_url = (base_url or settings.base_url).rstrip("/")
        self.session = session or requests.Session()
        self.token: str | None = None
        self.user: dict | None = None

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        headers = dict(kwargs.pop("headers", {}) or {})
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        response = self.session.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=settings.request_timeout,
            **kwargs,
        )
        log.info("%s %s -> %s (%.0f ms)", method, path, response.status_code, response.elapsed.total_seconds() * 1000)
        return response

    # Auth
    def login(self, username: str, password: str) -> requests.Response:
        response = self._request("POST", "/api/auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            body = response.json()
            self.token = body["access_token"]
            self.user = body["user"]
        return response

    def me(self) -> requests.Response:
        return self._request("GET", "/api/users/me")

    def health(self) -> requests.Response:
        return self._request("GET", "/api/health")

    # Tickets
    def list_tickets(self, **params) -> requests.Response:
        return self._request("GET", "/api/tickets", params=params)

    def create_ticket(self, payload: dict) -> requests.Response:
        return self._request("POST", "/api/tickets", json=payload)

    def get_ticket(self, ticket_id: int) -> requests.Response:
        return self._request("GET", f"/api/tickets/{ticket_id}")

    def update_ticket(self, ticket_id: int, **fields) -> requests.Response:
        return self._request("PATCH", f"/api/tickets/{ticket_id}", json=fields)

    def delete_ticket(self, ticket_id: int) -> requests.Response:
        return self._request("DELETE", f"/api/tickets/{ticket_id}")

    def add_comment(self, ticket_id: int, body: str) -> requests.Response:
        return self._request("POST", f"/api/tickets/{ticket_id}/comments", json={"body": body})

    # Admin
    def reset(self) -> requests.Response:
        return self._request("POST", "/api/admin/reset")

    def login_as(role):
        username, password = USERS[role]
        return username, password

    
