#!/usr/bin/env python3

import pathlib
import sys

from yoyo import get_backend, read_migrations

DATABASE_PATH = pathlib.Path.home() / ".local" / "share" / "lixue" / "knowledge.sqlite3"
MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"


def main() -> None:
    if not MIGRATIONS_DIR.is_dir():
        print(f"migrations directory not found: {MIGRATIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    backend = get_backend(f"sqlite:///{DATABASE_PATH}")
    migrations = read_migrations(str(MIGRATIONS_DIR))

    with backend.lock():
        to_apply = backend.to_apply(migrations)
        if not to_apply:
            print(f"database is up to date: {DATABASE_PATH}")
            return
        backend.apply_migrations(to_apply)
        print(f"applied {len(to_apply)} migration(s) to: {DATABASE_PATH}")


if __name__ == "__main__":
    main()
