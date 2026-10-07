from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import COOKIE_NAME, TOKEN_TTL_HOURS, create_token, get_optional_user, verify_password
from ..database import get_db
from ..models import Ticket, User

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


def _login_redirect() -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


@router.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/tickets", status_code=303)


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user:
        return RedirectResponse("/tickets", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", include_in_schema=False)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid credentials"}, status_code=401)
    response = RedirectResponse("/tickets", status_code=303)
    response.set_cookie(
        COOKIE_NAME,
        create_token(user),
        httponly=True,
        samesite="lax",
        max_age=TOKEN_TTL_HOURS * 3600,
    )
    return response


@router.get("/logout", include_in_schema=False)
def logout() -> RedirectResponse:
    response = _login_redirect()
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get("/tickets", response_class=HTMLResponse, include_in_schema=False)
def tickets_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user is None:
        return _login_redirect()
    return templates.TemplateResponse(request, "tickets.html", {"user": user})


@router.get("/widgets", response_class=HTMLResponse, include_in_schema=False)
def widgets_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user is None:
        return _login_redirect()
    return templates.TemplateResponse(request, "widgets.html", {"user": user})


@router.get("/widgets/frame", response_class=HTMLResponse, include_in_schema=False)
def widgets_frame(request: Request):
    return templates.TemplateResponse(request, "widgets_frame.html", {})


@router.get("/tickets/new", response_class=HTMLResponse, include_in_schema=False)
def new_ticket_page(request: Request, user: User | None = Depends(get_optional_user)):
    if user is None:
        return _login_redirect()
    return templates.TemplateResponse(request, "ticket_form.html", {"user": user})


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse, include_in_schema=False)
def ticket_detail_page(
    ticket_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    if user is None:
        return _login_redirect()
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        return templates.TemplateResponse(request, "not_found.html", {"user": user}, status_code=404)
    agents = db.scalars(select(User).where(User.role.in_(["admin", "agent"]))).all()
    return templates.TemplateResponse(
        request,
        "ticket_detail.html",
        {"user": user, "ticket": ticket, "agents": agents},
    )