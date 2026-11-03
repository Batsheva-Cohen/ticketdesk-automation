import pytest

from clients.api_client import ApiClient
from utils.config import ALL_PRIORITIES, ALL_STATUSES
from utils.data_factory import ticket_payload

pytestmark = [pytest.mark.api]

TICKET_KEYS = {
    "id",
    "title",
    "description",
    "priority",
    "status",
    "reporter",
    "assignee",
    "created_at",
    "updated_at",
    "comments_count",
}


@pytest.mark.smoke
def test_create_ticket_returns_201_with_expected_shape(reporter_api: ApiClient, admin_api: ApiClient):
    payload = ticket_payload(priority="high")
    response = reporter_api.create_ticket(payload)
    assert response.status_code == 201
    ticket = response.json()
    try:
        assert set(ticket) == TICKET_KEYS
        assert ticket["title"] == payload["title"]
        assert ticket["priority"] == "high"
        assert ticket["status"] == "open", "new tickets always start as open"
        assert ticket["reporter"]["username"] == "reporter"
        assert ticket["assignee"] is None
        assert ticket["comments_count"] == 0
    finally:
        admin_api.delete_ticket(ticket["id"])


@pytest.mark.parametrize(
    "field, value, expected_message",
    [
        ("title", "ab", "String should have at least 3 characters"),
        ("description", "too short", "String should have at least 10 characters"),
        ("priority", "urgent", "Input should be 'low', 'medium', 'high' or 'critical'"),
    ],
    ids=["title-too-short", "description-too-short", "priority-not-in-enum"],
)
def test_create_ticket_validation_errors(agent_api: ApiClient, field: str, value, expected_message: str):
    response = agent_api.create_ticket(ticket_payload(**{field: value}))
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == field and error["msg"] == expected_message for error in errors), errors


def test_create_ticket_requires_authentication(anonymous_api: ApiClient):
    response = anonymous_api.create_ticket(ticket_payload())
    assert response.status_code == 401


def test_get_ticket_by_id(ticket_factory, agent_api: ApiClient):
    created = ticket_factory()
    response = agent_api.get_ticket(created["id"])
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["comments"] == []


def test_get_missing_ticket_returns_404(agent_api: ApiClient):
    response = agent_api.get_ticket(999_999)
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_list_default_pagination(agent_api: ApiClient):
    response = agent_api.list_tickets()
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert len(body["items"]) == 10
    assert body["total"] >= 25, "seed data contains 25 tickets"


def test_list_is_sorted_by_created_at_desc_by_default(agent_api: ApiClient):
    items = agent_api.list_tickets(page_size=50).json()["items"]
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.parametrize("status", ALL_STATUSES)
def test_list_filter_by_status_returns_only_matching(agent_api: ApiClient, status: str):
    items = agent_api.list_tickets(status=status, page_size=50).json()["items"]
    assert items, f"seed data should contain at least one {status} ticket"
    assert {item["status"] for item in items} == {status}


@pytest.mark.parametrize("priority", ALL_PRIORITIES)
def test_list_filter_by_priority(agent_api: ApiClient, priority: str):
    items = agent_api.list_tickets(priority=priority, page_size=50).json()["items"]
    assert {item["priority"] for item in items} == {priority}


def test_list_rejects_page_size_above_limit(agent_api: ApiClient):
    response = agent_api.list_tickets(page_size=51)
    assert response.status_code == 422


def test_search_matches_title(ticket_factory, agent_api: ApiClient):
    ticket = ticket_factory(title="Zebra-unique-title for search")
    items = agent_api.list_tickets(q="Zebra-unique").json()["items"]
    assert [item["id"] for item in items] == [ticket["id"]]

@pytest.mark.xfail(reason="BUG-002: search ignores description, see docs/BUG_REPORTS.md", strict=True)
def test_search_matches_description(ticket_factory, agent_api: ApiClient):
    # Spec: search covers title OR description.
    ticket = ticket_factory(description="Contains the word Quokka-marker somewhere inside.")
    items = agent_api.list_tickets(q="Quokka-marker").json()["items"]
    assert [item["id"] for item in items] == [ticket["id"]]


def test_reporter_cannot_update_ticket(ticket_factory, reporter_api: ApiClient):
    ticket = ticket_factory()
    response = reporter_api.update_ticket(ticket["id"], status="in_progress")
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_assign_ticket_to_agent(ticket_factory, admin_api: ApiClient, agent_api: ApiClient):
    ticket = ticket_factory()
    response = admin_api.update_ticket(ticket["id"], assignee_id=agent_api.user["id"])
    assert response.status_code == 200
    assert response.json()["assignee"]["username"] == "agent"


def test_cannot_assign_ticket_to_reporter(ticket_factory, admin_api: ApiClient, reporter_api: ApiClient):
    ticket = ticket_factory()
    response = admin_api.update_ticket(ticket["id"], assignee_id=reporter_api.user["id"])
    assert response.status_code == 400


@pytest.mark.parametrize("client_fixture", ["agent_api", "reporter_api"])
def test_only_admin_can_delete(request, ticket_factory, client_fixture: str):
    client: ApiClient = request.getfixturevalue(client_fixture)
    ticket = ticket_factory()
    assert client.delete_ticket(ticket["id"]).status_code == 403


def test_admin_delete_removes_ticket(ticket_factory, admin_api: ApiClient):
    ticket = ticket_factory()
    assert admin_api.delete_ticket(ticket["id"]).status_code == 204
    assert admin_api.get_ticket(ticket["id"]).status_code == 404


def test_add_comment_increments_count(ticket_factory, reporter_api: ApiClient):
    ticket = ticket_factory()
    response = reporter_api.add_comment(ticket["id"], "Looks related to the caching layer.")
    assert response.status_code == 201
    assert response.json()["author"]["username"] == "reporter"
    detail = reporter_api.get_ticket(ticket["id"]).json()
    assert detail["comments_count"] == 1
    assert detail["comments"][0]["body"] == "Looks related to the caching layer."


def test_empty_comment_is_rejected(ticket_factory, reporter_api: ApiClient):
    ticket = ticket_factory()
    assert reporter_api.add_comment(ticket["id"], "").status_code == 422

@pytest.mark.xfail(reason="BUG-003: Validation Bug: System accepts ticket titles exceeding the 81-character limit see docs/BUG_REPORTS.md", strict=True)
def test_create_ticket_title_too_long_returns_422(agent_api: ApiClient):
    payload = ticket_payload(title="a" * 81)
    response = agent_api.create_ticket(payload)
    assert response.status_code == 422

def test_create_ticket_title_regular_returns_201(agent_api: ApiClient):
    payload = ticket_payload(title="a" * 12)
    response = agent_api.create_ticket(payload)
    assert response.status_code == 201

@pytest.mark.xfail(reason="Bug 004: Priority sorting is alphabetical (critical, high, low, medium) instead of logical severity")
def test_list_sort_by_priority_asc(agent_api: ApiClient):
    items = agent_api.list_tickets(sort="priority", order="asc", page_size=50).json()["items"]
    priorities = [item["priority"] for item in items]
    assert priorities == sorted(priorities)


def test_list_pagination_page_3(agent_api: ApiClient):

    response = agent_api.list_tickets(page=3, page_size=10)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert data["page"] == 3
    assert data["page_size"] == 10
    assert len(data["items"]) == 7
    assert data["total"] >= 25


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0, "page_size": 10},
        {"page": 1, "page_size": 0},  
    ]
)
def test_list_invalid_pagination_returns_422(agent_api: ApiClient, params: dict):
    response = agent_api.list_tickets(**params)
    assert response.status_code == 422

def test_list_tickets_requires_authentication(anonymous_api: ApiClient):
    response = anonymous_api.list_tickets()
    assert response.status_code == 401

def test_assign_ticket_to_non_existent_assignee_returns_400(agent_api: ApiClient, ticket_factory):
    ticket = ticket_factory()
    ticket_id = ticket["id"]
    response = agent_api.update_ticket(ticket_id, assignee_id=9999)
    assert response.status_code == 400


def test_reporter_can_add_comment_to_admin_ticket(admin_api: ApiClient, reporter_api: ApiClient):   
    payload = ticket_payload(title="Bug in production", description="Created by admin user")
    ticket_response = admin_api.create_ticket(payload)
    assert ticket_response.status_code == 201
    
    ticket_id = ticket_response.json()["id"]
    comment_content = "reporter_update"
    comment_response = reporter_api.add_comment(ticket_id, comment_content)
    
    assert comment_response.status_code == 201    
    comment_data = comment_response.json()
    print(comment_data)
    assert comment_data["body"] == comment_content
    assert comment_data["author"]["role"] == "reporter"  #