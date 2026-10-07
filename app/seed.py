from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .auth import hash_password
from .models import Comment, Ticket, User, utcnow

DEFAULT_USERS = [
    {"username": "admin", "password": "Admin123!", "role": "admin"},
    {"username": "agent", "password": "Agent123!", "role": "agent"},
    {"username": "reporter", "password": "Reporter123!", "role": "reporter"},
]

SEED_TICKETS = [
    ("Login button unresponsive on Safari", "Clicking Sign in does nothing on Safari 17.", "high", "open"),
    ("Typo on the pricing page", "The word 'recieve' should be 'receive' in the FAQ block.", "low", "open"),
    ("Export to CSV drops the last row", "Exporting 50 rows produces a file with 49 rows.", "critical", "in_progress"),
    ("Dark mode toggle resets on refresh", "The theme preference is not persisted between reloads.", "medium", "open"),
    (
        "Search returns stale results",
        "After deleting an item it still appears in search for a minute.",
        "high",
        "in_progress",
    ),
    ("Password reset email delayed", "Reset emails arrive 10 minutes late during peak hours.", "high", "resolved"),
    ("Profile picture upload fails for PNG", "PNG files above 2MB return a 500 error.", "medium", "closed"),
    ("Dashboard chart overlaps legend", "On 1366px width the legend covers the last bar.", "low", "closed"),
    (
        "Notifications badge shows wrong count",
        "Badge shows 3 while only 2 unread notifications exist.",
        "medium",
        "open",
    ),
    ("API rate limit too aggressive", "Clients get 429 after 20 requests instead of 100.", "critical", "open"),
    ("Mobile menu does not close", "Tapping outside the drawer leaves it open on Android.", "medium", "in_progress"),
    ("Invoice PDF missing VAT line", "Generated invoices omit the VAT breakdown line.", "high", "resolved"),
    ("Slow load on tickets list", "The list takes 6 seconds to render with 500 tickets.", "high", "open"),
    ("Date picker allows past dates", "Due date field accepts dates in the past.", "low", "open"),
    ("Tooltip text cut off", "Long tooltips are truncated without ellipsis.", "low", "closed"),
    ("Session expires too early", "Users are logged out after 5 minutes of inactivity.", "critical", "in_progress"),
    ("Broken link in footer", "Terms of service link returns 404.", "low", "resolved"),
    ("Duplicate emails on signup", "Two welcome emails are sent for each new account.", "medium", "open"),
    ("Sorting by priority is inconsistent", "Critical appears between low and medium.", "medium", "open"),
    ("Autosave loses draft", "Draft is lost when the browser tab is closed.", "high", "open"),
    ("Keyboard navigation skips buttons", "Tab order skips the Save button in the modal.", "medium", "resolved"),
    ("Timezone shown incorrectly", "Timestamps display UTC instead of local time.", "low", "in_progress"),
    ("Filter chips not removable", "Clicking the x on a filter chip has no effect.", "medium", "open"),
    ("Comment markdown not rendered", "Bold and links appear as raw markdown.", "low", "open"),
    ("Crash when title is empty", "Submitting the form with an empty title crashes the page.", "critical", "resolved"),
]


def reset_database(db: Session) -> None:
    db.execute(delete(Comment))
    db.execute(delete(Ticket))
    db.execute(delete(User))
    db.commit()
    seed_database(db)


def seed_database(db: Session) -> None:
    users = {}
    for spec in DEFAULT_USERS:
        user = User(
            username=spec["username"],
            password_hash=hash_password(spec["password"]),
            role=spec["role"],
        )
        db.add(user)
        users[spec["role"]] = user
    db.flush()

    base_time = utcnow() - timedelta(days=30)
    for index, (title, description, priority, status) in enumerate(SEED_TICKETS):
        reporter = users["reporter"] if index % 3 else users["agent"]
        assignee = users["agent"] if status != "open" else None
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            status=status,
            reporter_id=reporter.id,
            assignee_id=assignee.id if assignee else None,
            created_at=base_time + timedelta(days=index, hours=index % 5),
            updated_at=base_time + timedelta(days=index, hours=index % 5),
        )
        db.add(ticket)
        db.flush()
        if index % 4 == 0:
            db.add(Comment(ticket_id=ticket.id, author_id=users["agent"].id, body="Reproduced locally, investigating."))
        if index % 6 == 0:
            db.add(Comment(ticket_id=ticket.id, author_id=users["admin"].id, body="Escalating to the platform team."))
    db.commit()


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(User).limit(1)) is None:
        seed_database(db)