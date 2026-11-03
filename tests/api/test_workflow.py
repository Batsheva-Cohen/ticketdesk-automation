import pytest

from clients.api_client import ApiClient
from utils.config import ALL_STATUSES, VALID_TRANSITIONS

pytestmark = [pytest.mark.api, pytest.mark.workflow]

# Build every (from, to) pair once so the parametrization is data driven.
VALID_PAIRS = [(src, dst) for src, targets in VALID_TRANSITIONS.items() for dst in sorted(targets)]
INVALID_PAIRS = [
    (src, dst) for src in ALL_STATUSES for dst in ALL_STATUSES if dst != src and dst not in VALID_TRANSITIONS[src]
]

# Shortest path from "open" to every status, used to prepare the starting state.
PATH_TO = {
    "open": [],
    "in_progress": ["in_progress"],
    "resolved": ["in_progress", "resolved"],
    "closed": ["in_progress", "resolved", "closed"],
}


def move_ticket_to(client: ApiClient, ticket_id: int, status: str) -> None:
    for step in PATH_TO[status]:
        response = client.update_ticket(ticket_id, status=step)
        assert response.status_code == 200, f"setup step {step} failed: {response.text}"


@pytest.mark.parametrize("source, target", VALID_PAIRS, ids=[f"{s}->{t}" for s, t in VALID_PAIRS])
def test_valid_transition_is_accepted(ticket_factory, agent_api: ApiClient, source: str, target: str):
    ticket = ticket_factory()
    move_ticket_to(agent_api, ticket["id"], source)
    response = agent_api.update_ticket(ticket["id"], status=target)
    assert response.status_code == 200
    assert response.json()["status"] == target

INVALID_PAIRS_PARAMS = [
    pytest.param(src, dst, marks=pytest.mark.xfail(reason="BUG-001: closed is not final", strict=True))
    if (src, dst) == ("closed", "open")
    else pytest.param(src, dst)
    for src, dst in INVALID_PAIRS
]
@pytest.mark.parametrize("source, target", INVALID_PAIRS_PARAMS, ids=[f"{s}->{t}" for s, t in INVALID_PAIRS])
def test_invalid_transition_returns_409(ticket_factory, agent_api: ApiClient, source: str, target: str):
    ticket = ticket_factory()
    move_ticket_to(agent_api, ticket["id"], source)
    response = agent_api.update_ticket(ticket["id"], status=target)
    assert response.status_code == 409
    assert response.json()["detail"] == f"Invalid transition from {source} to {target}"
    assert agent_api.get_ticket(ticket["id"]).json()["status"] == source, "status must not change"


def test_same_status_is_a_noop(ticket_factory, agent_api: ApiClient):
    ticket = ticket_factory()
    response = agent_api.update_ticket(ticket["id"], status="open")
    assert response.status_code == 200
    assert response.json()["status"] == "open"


def test_updated_at_behavior_on_transition_vs_noop(ticket_factory, agent_api: ApiClient):
    ticket = ticket_factory()
    assert ticket["status"] == "open"
    ticket_id = ticket["id"]
    initial_updated_at = agent_api.get_ticket(ticket_id).json()["updated_at"]
    response = agent_api.update_ticket(ticket_id, status="in_progress")
    assert response.json()["updated_at"] != initial_updated_at
    noop_response = agent_api.update_ticket(ticket_id, status="in_progress")
    assert noop_response.json()["updated_at"] == response.json()["updated_at"]


def test_update_status_and_assignee(ticket_factory, agent_api: ApiClient):    
    ticket = ticket_factory()
    ticket_id = ticket["id"]
    response = agent_api.update_ticket(ticket_id, status = "in_progress", assignee_id = 2 ) 
    assert response.status_code == 200, f"Failed to update ticket: {response.text}"
    updated_ticket = agent_api.get_ticket(ticket_id).json()
    assert updated_ticket["status"] == "in_progress"
    assert updated_ticket["assignee"]["id"] == 2
