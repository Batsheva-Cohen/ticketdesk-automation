import sqlite3
from contextlib import contextmanager
from typing import Any

from .config import settings


@contextmanager
def connect():
    connection = sqlite3.connect(settings.db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    with connect() as connection:
        return connection.execute(sql, params).fetchall()


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> sqlite3.Row | None:
    with connect() as connection:
        return connection.execute(sql, params).fetchone()


def scalar(sql: str, params: tuple[Any, ...] = ()) -> Any:
    row = fetch_one(sql, params)
    return None if row is None else row[0]