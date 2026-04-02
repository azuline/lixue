from __future__ import annotations

import contextlib
import pathlib
import sqlite3
from collections.abc import Iterator

from yoyo import get_backend, read_migrations

DATABASE_PATH = pathlib.Path.home() / ".local" / "share" / "lixue" / "knowledge.sqlite3"
MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"


@contextlib.contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(
        DATABASE_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES,
        isolation_level=None,
        timeout=15.0,
    )
    try:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        yield conn
    finally:
        conn.close()


def migrate(database_path: pathlib.Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    backend = get_backend(f"sqlite:///{database_path}")
    migrations = read_migrations(str(MIGRATIONS_DIR))
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))
