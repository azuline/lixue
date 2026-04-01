# Database

The database lives at `~/.local/share/lixue/knowledge.sqlite3`. Run `scripts/database-migrate.py` to create and migrate it.

## Connection conventions

All connections use:

- `row_factory = sqlite3.Row` (dict-like row access)
- `PRAGMA foreign_keys=ON`
- `PRAGMA journal_mode=WAL`
- `isolation_level=None` (autocommit; use explicit `BEGIN`/`COMMIT`)

## Migrations

Migrations live in `migrations/` and are plain Python files using
`yoyo.step()`.

Create at most one migration per branch. If the current branch already has a
migration, update it in-place instead of adding a new one.

```python
from yoyo import step

step(
    "CREATE TABLE ...",
    "DROP TABLE ...",
)
```

## Versioned table conventions

Root entity tables are suffixed `_versioned` and store every version of a row.
Views on top present the latest data. Each versioned table has:

- `version INTEGER NOT NULL` (incrementing per entity)
- `inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))`
- `updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))`
- `deleted INTEGER NOT NULL DEFAULT 0` (soft deletion tombstone on root entities)

```sql
CREATE TABLE new_things_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    -- entity fields here --
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version)
);

CREATE VIEW new_things AS
SELECT v.*
FROM new_things_versioned v
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM new_things_versioned
    GROUP BY id
) latest ON v.id = latest.id AND v.version = latest.max_version
WHERE v.deleted = 0;
```

## Junction / subtable conventions

Junction tables (many-to-many relationships, subtables) are not versioned. They
have a simple autoincrement `id`, timestamps, and unique constraints:

```sql
CREATE TABLE parent_children (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL,
    child_id INTEGER NOT NULL,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    FOREIGN KEY (parent_id) REFERENCES parents_versioned(id),
    FOREIGN KEY (child_id) REFERENCES children_versioned(id),
    UNIQUE (parent_id, child_id)
);
```

## Enum table conventions

Express enums as enum tables with a `value TEXT PRIMARY KEY`:

```sql
CREATE TABLE new_kind_enum (value TEXT PRIMARY KEY NOT NULL);
INSERT INTO new_kind_enum (value) VALUES ('value1'), ('value2');
-- Usage: some_column TEXT NOT NULL REFERENCES new_kind_enum(value)
```

## Column conventions

- Use `INTEGER` for IDs (SQLite autoincrement).
- Use `TEXT` for strings, dates (ISO 8601), and JSON arrays (serialized as JSON text).
- Foreign keys reference the `_versioned` table's `id` column (not the view).
- All tables have `inserted_at` and `updated_at` with the strftime default.

 Dev loop

```bash
just lint      # auto-fix: ruff format + ruff check --fix
just lintcheck # check without fixing
```

# Dev environment

Managed via Nix flakes. Enter the dev shell with `nix develop` or use direnv
(`.envrc` calls `use flake`). The dev shell provides:

- Python 3.13 with yoyo-migrations
- ruff (linter/formatter)
- just (command runner)

 Design patterns

# Dataclasses

Use `@dataclasses.dataclass(slots=True)` for data containers. Reserve classic
classes for third-party interfaces. NEVER use a raw dict as a data container
when the keys are statically known. ALWAYS use a dataclass.

# Private functions

Prefix all module-private symbols (functions, constants, classes, methods) with
`_`. When unsure, mark it private. Put module-private code at the BOTTOM of the
file, **NOT THE TOP**. Public exports go at the top.

# Parse, don't validate

Combine data parsing and validation into single functions that return structured
dataclasses.

# Errors

Error messages must be lowercase phrases separated by colons:

```python
raise SomeError("failed to read file: file not found", path=path)
```

## Error handling

We have a robust system that does not tolerate undefined behaviors:

1. Fail fast. Do not silently skip, fallback, or continue unless instructed.
2. Do not catch exceptions unnecessarily; let them bubble up so issues can be
   observed and debugged.
3. NEVER use general try/except blocks that silence errors. Only catch specific
   exceptions when you have a concrete plan to handle them.
4. NEVER catch a bare `Exception`. ONLY catch specific errors.
5. Do NOT allow for graceful degradation. The code path should succeed OR raise
   an error.

 Legibility

# Docstrings

Do NOT write docstrings. The human programmer will write high-quality bespoke
docstrings once you are done with your work. **DO NOT WRITE DOCSTRINGS.**

# Imports

For standard library and third-party dependencies, import full modules rather
than individual functions unless the function name is unique or the import path
has three-or-more parts.

```python
 Prefer
import dataclasses
@dataclasses.dataclass(slots=True)

 Over
from dataclasses import dataclass
```

# Scripts

Executable scripts live in `scripts/`. Each script is a standalone `chmod +x`
Python file with a `#!/usr/bin/env python3` shebang. Scripts should be
self-contained and import only from the standard library and dependencies
available in the Nix dev shell.
