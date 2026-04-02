from __future__ import annotations

import pathlib
import subprocess

from conftest import LixueFixture
from foundation.database import connect

nl = "\n"


def test_versioned_tables_have_required_columns(t: LixueFixture) -> None:
    with connect(t.db_path) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_versioned'").fetchall()]

    failing = []
    for table in tables:
        with connect(t.db_path) as conn:
            columns = {row[1]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

        required = {
            "id": ("INTEGER", True),
            "version": ("INTEGER", True),
            "inserted_at": ("TEXT", True),
            "updated_at": ("TEXT", True),
            "deleted": ("BOOLEAN", True),
        }
        for col_name, (expected_type, expected_notnull) in required.items():
            if col_name not in columns:
                failing.append(f"{table}: missing column `{col_name}`")
                continue
            col = columns[col_name]
            # col: cid, name, type, notnull, dflt_value, pk
            if col[2] != expected_type:
                failing.append(f"{table}.{col_name}: expected type {expected_type}, got {col[2]}")
            if bool(col[3]) != expected_notnull:
                failing.append(f"{table}.{col_name}: expected notnull={expected_notnull}")

        # Check PK is (id, version).
        pk_columns = {col[1] for col in columns.values() if col[5] > 0}
        if pk_columns != {"id", "version"}:
            failing.append(f"{table}: expected PRIMARY KEY (id, version), got {pk_columns}")

    assert not failing, f"Versioned table convention violations:\n{nl.join(f'- {f}' for f in failing)}"


def test_versioned_tables_have_views(t: LixueFixture) -> None:
    with connect(t.db_path) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE '%_versioned'").fetchall()]
        views = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'view'").fetchall()}

    failing = []
    for table in tables:
        view_name = table.removesuffix("_versioned")
        if view_name not in views:
            failing.append(f"{table}: missing companion view `{view_name}`")

    assert not failing, f"Missing views for versioned tables:\n{nl.join(f'- {f}' for f in failing)}"


def test_junction_tables_have_required_columns(t: LixueFixture) -> None:
    with connect(t.db_path) as conn:
        all_tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '_yoyo%' AND name NOT LIKE 'yoyo%'").fetchall()]

    junction_tables = [t_name for t_name in all_tables if not t_name.endswith("_versioned") and not t_name.endswith("_enum")]

    failing = []
    for table in junction_tables:
        with connect(t.db_path) as conn:
            columns = {row[1]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

        # Must have deleted and inserted_at.
        if "deleted" not in columns:
            failing.append(f"{table}: missing column `deleted`")
        elif columns["deleted"][2] != "BOOLEAN":
            failing.append(f"{table}.deleted: expected type BOOLEAN, got {columns['deleted'][2]}")

        if "inserted_at" not in columns:
            failing.append(f"{table}: missing column `inserted_at`")

        # Must NOT have updated_at (junction rows are immutable).
        if "updated_at" in columns:
            failing.append(f"{table}: junction tables should not have `updated_at` (rows are immutable)")

        # Must have a *_version column (tied to parent entity version).
        version_cols = [name for name in columns if name.endswith("_version")]
        if not version_cols:
            failing.append(f"{table}: missing parent version column (expected a column ending in `_version`)")

    assert not failing, f"Junction table convention violations:\n{nl.join(f'- {f}' for f in failing)}"


def test_timestamp_columns_have_defaults(t: LixueFixture) -> None:
    with connect(t.db_path) as conn:
        all_tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '_yoyo%' AND name NOT LIKE 'yoyo%' AND name NOT LIKE '%_enum'").fetchall()]

    failing = []
    for table in all_tables:
        with connect(t.db_path) as conn:
            columns = {row[1]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}

        for col_name in ("inserted_at", "updated_at"):
            if col_name not in columns:
                continue
            col = columns[col_name]
            dflt = col[4] or ""
            if "strftime" not in dflt:
                failing.append(f"{table}.{col_name}: expected DEFAULT containing strftime, got `{dflt}`")
            if not col[3]:
                failing.append(f"{table}.{col_name}: expected NOT NULL")

    assert not failing, f"Timestamp column violations:\n{nl.join(f'- {f}' for f in failing)}"


def test_id_columns_are_foreign_keys(t: LixueFixture) -> None:
    with connect(t.db_path) as conn:
        all_tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '_yoyo%' AND name NOT LIKE 'yoyo%' AND name NOT LIKE '%_enum'").fetchall()]

    failing = []
    for table in all_tables:
        with connect(t.db_path) as conn:
            columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            fk_columns = {row[3] for row in conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()}

        id_columns = {c for c in columns if c.endswith("_id")}
        non_fk_id_columns = id_columns - fk_columns
        for col in sorted(non_fk_id_columns):
            failing.append(f"{table}.{col}")

    assert not failing, f"Columns ending in `_id` should be foreign keys:\n{nl.join(f'- {f}' for f in failing)}"


def test_no_modified_migrations() -> None:
    migrations_dir = pathlib.Path(__file__).resolve().parent.parent / "migrations"

    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
    current_branch = result.stdout.strip()
    if current_branch in ("main", "master"):
        base_ref = "HEAD^"
    else:
        result = subprocess.run(["git", "rev-parse", "--verify", "main"], capture_output=True, text=True)
        base_ref = "main" if result.returncode == 0 else "master"

    result = subprocess.run(["git", "ls-tree", "-r", "--name-only", base_ref, "."], capture_output=True, text=True, check=True, cwd=migrations_dir)
    base_migrations = {line.strip() for line in result.stdout.splitlines() if line.strip().endswith(".sql")}

    result = subprocess.run(["git", "diff", "--relative", "--name-only", base_ref, "HEAD", "."], capture_output=True, text=True, check=True, cwd=migrations_dir)
    modified_files = {line.strip() for line in result.stdout.splitlines() if line.strip()}

    modified_existing = [f for f in modified_files if f in base_migrations]
    assert not modified_existing, f"Pre-existing migration files should never be modified:\n{nl.join(f'- {f}' for f in modified_existing)}"
