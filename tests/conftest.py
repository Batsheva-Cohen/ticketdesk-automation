import os
import threading
import time

import pytest
import requests

from clients.api_client import ApiClient
from utils.config import USERS, settings
from utils.data_factory import ticket_payload


def _app_is_up(base_url: str) -> bool:
    try:
        return requests.get(f"{base_url}/api/health", timeout=2).status_code == 200
    except requests.RequestException:
        return False


@pytest.fixture(scope="session", autouse=True)
def app_server():
    """Start TicketDesk inside the test process when it is not already running.

    Locally the app is usually started manually with uvicorn. In CI (or when
    TICKETDESK_AUTOSTART=1) this fixture boots it in a background thread so a
    single `pytest` command is enough.
    """
    if _app_is_up(settings.base_url) or not settings.autostart_app:
        yield
        return

    worker = os.getenv("PYTEST_XDIST_WORKER")
    if worker and worker != "gw0":
        # Under pytest-xdist only the first worker boots the app; the rest wait for it.
        for _ in range(100):
            if _app_is_up(settings.base_url):
                break
            time.sleep(0.3)
        yield
        return

    import uvicorn

    from app.main import app

    host, port = settings.base_url.replace("http://", "").split(":")
    config = uvicorn.Config(app, host=host, port=int(port), log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if _app_is_up(settings.base_url):
            break
        time.sleep(0.2)
    else:
        raise RuntimeError(f"TicketDesk did not start on {settings.base_url}")
    yield
    server.should_exit = True
    thread.join(timeout=5)


def _logged_in_client(role: str) -> ApiClient:
    username, password = USERS[role]
    client = ApiClient()
    response = client.login(username, password)
    assert response.status_code == 200, f"Login as {role} failed: {response.text}"
    return client


@pytest.fixture(scope="session")
def admin_api() -> ApiClient:
    """
    Returns an ApiClient already successfully logged in as an administrator (Admin)
    """
    return _logged_in_client("admin")


@pytest.fixture(scope="session")
def agent_api() -> ApiClient:
    """
    Returns an ApiClient already successfully logged in as an agent
    """
    return _logged_in_client("agent")


@pytest.fixture(scope="session")
def reporter_api() -> ApiClient:
    """
    Returns an ApiClient already successfully logged in as an reporter
    """
    return _logged_in_client("reporter")


@pytest.fixture
def anonymous_api() -> ApiClient:
    """
    Used for an unauthenticated client
    """
    return ApiClient()


@pytest.fixture(scope="session", autouse=True)
def clean_database(app_server, admin_api):
    """Reseed the database once per session so every run starts from a known state.

    In parallel runs (pytest -n) the reset is done once by scripts/run_tests.sh
    before pytest starts, otherwise workers would wipe each other's data.
    """
    if os.getenv("PYTEST_XDIST_WORKER") is None:
        response = admin_api.reset()
        assert response.status_code == 200, response.text
    yield


@pytest.fixture
def ticket_factory(admin_api, agent_api):
    """Create tickets through the API and delete them after the test.

    Usage: ticket = ticket_factory(priority="high") -> dict of the created ticket.
    """
    created_ids: list[int] = []

    def _create(client: ApiClient | None = None, **overrides) -> dict:
        response = (client or agent_api).create_ticket(ticket_payload(**overrides))
        assert response.status_code == 201, response.text
        ticket = response.json()
        created_ids.append(ticket["id"])
        return ticket

    yield _create

    for ticket_id in created_ids:
        admin_api.delete_ticket(ticket_id)


# Reporting hooks -----------------------------------------------------------


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot of the failing page to the pytest-html report.

    pytest-playwright already saves screenshots to test-results/; this hook embeds
    the same image in report.html so a failure is readable without opening folders.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return
    page = item.funcargs.get("page") or item.funcargs.get("agent_page") or item.funcargs.get("admin_page")
    page = page or item.funcargs.get("reporter_page")
    if page is None:
        return
    try:
        image = page.screenshot(full_page=True)
    except Exception:  # the browser may already be closed
        return
    extras = getattr(report, "extras", [])
    try:
        from pytest_html import extras as html_extras

        extras.append(html_extras.png(image, name="failure"))
        report.extras = extras
    except ImportError:
        pass
    try:
        import allure

        allure.attach(image, name="failure screenshot", attachment_type=allure.attachment_type.PNG)
    except ImportError:
        pass


# UI fixtures ---------------------------------------------------------------


@pytest.fixture(scope="session")
def base_url() -> str:
    # Overrides the pytest-base-url fixture so Playwright's page.goto("/tickets") works.
    return settings.base_url


@pytest.fixture
def login_as(context, base_url):
    """Log in through the API and inject the JWT cookie into the browser context.

    This skips the login form for tests that are not about login, which keeps
    them fast and independent of the login page.
    """

    def _login(role: str):
        username, password = USERS[role]
        client = ApiClient()
        assert client.login(username, password).status_code == 200
        context.add_cookies([{"name": "access_token", "value": client.token, "url": base_url}])
        return client

    return _login


@pytest.fixture
def login_as_token():
    """Return a JWT for a role without touching any browser context."""

    def _token(role: str) -> str:
        username, password = USERS[role]
        client = ApiClient()
        assert client.login(username, password).status_code == 200
        return client.token

    return _token


@pytest.fixture
def admin_page(page, login_as):
    """
    Provides a browser page logged in as a admin user
    """
    login_as("admin")
    return page


@pytest.fixture
def agent_page(page, login_as):
    """
    Provides a browser page logged in as a agent user
    """
    login_as("agent")
    return page


@pytest.fixture
def reporter_page(page, login_as):
    """
    Provides a browser page logged in as a reporter user
    """
    login_as("reporter")
    return page