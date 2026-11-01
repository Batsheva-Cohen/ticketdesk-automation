import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("TICKETDESK_BASE_URL", "http://127.0.0.1:8000")
    db_path: str = os.getenv("TICKETDESK_DB_PATH", "./ticketdesk.db")
    autostart_app: bool = os.getenv("TICKETDESK_AUTOSTART", "1") == "1"
    request_timeout: int = 10


USERS: dict[str, tuple[str, str]] = {
    "admin": ("admin", "Admin123!"),
    "agent": ("agent", "Agent123!"),
    "reporter": ("reporter", "Reporter123!"),
}

VALID_TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress"},
    "in_progress": {"resolved", "open"},
    "resolved": {"closed", "open"},
    "closed": set(),
}

ALL_STATUSES = ("open", "in_progress", "resolved", "closed")
ALL_PRIORITIES = ("low", "medium", "high", "critical")

settings = Settings()