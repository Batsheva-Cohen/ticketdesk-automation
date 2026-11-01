import uuid


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]


def unique_title(prefix: str = "AUTO") -> str:
    return f"{prefix}-{unique_suffix()} automated ticket"


def ticket_payload(**overrides) -> dict:
    payload = {
        "title": unique_title(),
        "description": "Created by the automation framework. Steps: open app, reproduce, observe.",
        "priority": "medium",
    }
    payload.update(overrides)
    return payload

def comment_body():
    return f"Automated test comment {uuid.uuid4().hex[:8]}"
