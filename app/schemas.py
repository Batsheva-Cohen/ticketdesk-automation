from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["low", "medium", "high", "critical"]
Status = Literal["open", "in_progress", "resolved", "closed"]


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TicketCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=10)
    priority: Priority = "medium"


class TicketUpdate(BaseModel):
    status: Status | None = None
    assignee_id: int | None = None


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    body: str
    author: UserOut
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: str
    status: str
    reporter: UserOut
    assignee: UserOut | None
    created_at: datetime
    updated_at: datetime
    comments_count: int


class TicketDetail(TicketOut):
    comments: list[CommentOut]


class TicketList(BaseModel):
    items: list[TicketOut]
    total: int
    page: int
    page_size: int
