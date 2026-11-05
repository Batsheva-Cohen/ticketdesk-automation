import pytest

from clients.api_client import ApiClient
from tests.conftest import clean_database
from utils import db

pytestmark = [pytest.mark.db]


def test_api_total_matches_database_count(agent_api: ApiClient):
    api_total = agent_api.list_tickets().json()["total"]
    db_total = db.scalar("SELECT COUNT(*) FROM tickets")
    assert api_total == db_total


def test_created_ticket_is_persisted_with_reporter(ticket_factory, reporter_api: ApiClient):
    ticket = ticket_factory(reporter_api, priority="critical")
    row = db.fetch_one(
        "SELECT t.title, t.priority, t.status, u.username AS reporter "
        "FROM tickets t JOIN users u ON u.id = t.reporter_id WHERE t.id = ?",
        (ticket["id"],),
    )
    assert row is not None
    assert row["title"] == ticket["title"]
    assert row["priority"] == "critical"
    assert row["status"] == "open"
    assert row["reporter"] == "reporter"


def test_deleting_ticket_cascades_to_comments(ticket_factory, admin_api: ApiClient):
    ticket = ticket_factory()
    admin_api.add_comment(ticket["id"], "first")
    admin_api.add_comment(ticket["id"], "second")
    assert db.scalar("SELECT COUNT(*) FROM comments WHERE ticket_id = ?", (ticket["id"],)) == 2

    assert admin_api.delete_ticket(ticket["id"]).status_code == 204
    assert db.scalar("SELECT COUNT(*) FROM comments WHERE ticket_id = ?", (ticket["id"],)) == 0


def test_no_ticket_has_invalid_status_or_priority():
    bad_rows = db.fetch_all(
        "SELECT id, status, priority FROM tickets "
        "WHERE status NOT IN ('open','in_progress','resolved','closed') "
        "OR priority NOT IN ('low','medium','high','critical')"
    )
    assert bad_rows == []


def test_passwords_are_never_stored_in_plain_text():
    rows = db.fetch_all("SELECT username, password_hash FROM users")
    for row in rows:
        assert "$" in row["password_hash"], "expected salt$digest format"
        assert "123!" not in row["password_hash"], f"plain password leaked for {row['username']}"

def test_reset_endpoint_restores_initial_data(clean_database):
    num_of_tickets = db.scalar("SELECT COUNT(*) FROM tickets")
    num_of_count = db.scalar("SELECT COUNT(*) FROM users")
    assert num_of_tickets == 25
    assert num_of_count == 3

def test_all_assigned_users_have_valid_roles():
    invalid_assignments = db.fetch_all(
        "SELECT t.id AS ticket_id, u.username, u.role "
        "FROM tickets t JOIN users u ON u.id = t.assignee_id "
        "WHERE t.assignee_id IS NOT NULL AND u.role NOT IN ('agent', 'admin')"
    )
    assert invalid_assignments == []

def test_usernames_are_unique():
    duplicates = db.fetch_all(
        "SELECT username, COUNT(*) as count "
        "FROM users "
        "GROUP BY username "
        "HAVING COUNT(*) > 1"
    )
    assert duplicates == []