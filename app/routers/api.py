from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import create_token, get_current_user, require_roles, verify_password
from ..database import get_db
from ..models import Comment, Ticket, User
from ..schemas import (
    CommentCreate,
    CommentOut,
    LoginRequest,
    LoginResponse,
    Priority,
    Status,
    TicketCreate,
    TicketDetail,
    TicketList,
    TicketOut,
    TicketUpdate,
    UserOut,
)
from ..seed import reset_database

router = APIRouter(prefix="/api", tags=["api"])

# Allowed status transitions. "closed" is a final state according to the spec.
TRANSITIONS: dict[str, set[str]] = {
    "open": {"in_progress"},
    "in_progress": {"resolved", "open"},
    "resolved": {"closed", "open"},
    "closed": {"open"},
}


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return LoginResponse(access_token=create_token(user), user=UserOut.model_validate(user))


@router.get("/users/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/tickets", response_model=TicketList)
def list_tickets(
    status_filter: Status | None = Query(default=None, alias="status"),
    priority: Priority | None = None,
    q: str | None = Query(default=None, max_length=80),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    sort: Literal["id", "created_at", "priority", "status"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TicketList:
    query = select(Ticket)
    if status_filter:
        query = query.where(Ticket.status == status_filter)
    if priority:
        query = query.where(Ticket.priority == priority)
    if q:
        query = query.where(Ticket.title.contains(q))

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = getattr(Ticket, sort)
    ordering = sort_column.asc() if order == "asc" else sort_column.desc()
    items = db.scalars(query.order_by(ordering, Ticket.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return TicketList(
        items=[TicketOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/tickets", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(
    payload: TicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status="open",
        reporter_id=user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def _get_ticket_or_404(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")
    return ticket


@router.get("/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Ticket:
    return _get_ticket_or_404(db, ticket_id)


@router.patch("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "agent")),
) -> Ticket:
    ticket = _get_ticket_or_404(db, ticket_id)

    if payload.status is not None and payload.status != ticket.status:
        if payload.status not in TRANSITIONS[ticket.status]:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Invalid transition from {ticket.status} to {payload.status}",
            )
        ticket.status = payload.status

    if payload.assignee_id is not None:
        assignee = db.get(User, payload.assignee_id)
        if assignee is None or assignee.role not in ("admin", "agent"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Assignee must be an existing agent or admin")
        ticket.assignee_id = assignee.id

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> Response:
    ticket = _get_ticket_or_404(db, ticket_id)
    db.delete(ticket)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/tickets/{ticket_id}/comments",
    response_model=CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def add_comment(
    ticket_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Comment:
    ticket = _get_ticket_or_404(db, ticket_id)
    comment = Comment(ticket_id=ticket.id, author_id=user.id, body=payload.body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.post("/admin/reset")
def reset(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin")),
) -> dict:
    reset_database(db)
    return {"message": "reset done"}
