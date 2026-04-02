# Project structure

```
foundation/            # Shared libraries and utilities
migrations/            # yoyo migration files (source of truth for schema)
scripts/               # Executable scripts (chmod +x)
  database-migrate.py  # Create/migrate the knowledge database
tools/                 # Developer/AI tooling
```

# Dev loop

Run linting and tests after **every** milestone. Do not mark the milestone
complete until both pass. Take ownership over the whole codebase; even if
another programmer introduced the error, you should fix it.

```bash
just lint
just test [-vv]  # Use -vv when debugging test specific failures.
```

If you are debugging a failing test and trying to figure out why it is failing,
**always** start with running `just lint` and fixing any errors. This can solve
the problem.

`just help` lists common commands.

## Bespoke tooling

We leverage bespoke dev tools for developer experience. Add tools under
`tools/` as Python packages:

```
tools/my_tool/
  __init__.py          # empty
  __main__.py
```

Register each tool in the `justfile`.

Existing tools are:

- `just codegen-db` - Regenerate sqlc Python bindings and schema.sql from migrations.

# Design patterns

## Dataclasses

Use `@dataclasses.dataclass(slots=True)` for data containers. Reserve classic
classes for third-party interfaces. NEVER use a raw dict as a data container
when the keys are statically known. ALWAYS use a dataclass.

## Private functions

Prefix all module-private symbols (functions, constants, classes, methods) with
`_`. When unsure, mark it private. Put module-private code at the BOTTOM of the
file, **NOT THE TOP**. Public exports go at the top.

## Parse, don't validate

Follow the "parse, don't validate" principle by combining data parsing and
validation into single functions. Parse functions should return structured
dataclasses.

```python
# Instead of
validate_data(some_dict)
# uses some_dict


# Prefer
@dataclasses.dataclass
class StructuredData: ...


data = parse_structured_data(some_dict)
# uses data
```

## Errors

Error messages must be lowercase phrases separated by colons:

```python
raise SomeError("failed to read file: file not found", path=path)
```

### Error handling

We have a robust system that does not tolerate undefined behaviors:

1. Fail fast. Do not silently skip, fallback, or continue unless instructed.
2. Do not catch exceptions unnecessarily; let them bubble up so issues can be
   observed and debugged. Only catch exceptions when you have a specific
   recovery strategy.
3. NEVER use general try/except blocks that silence errors. Only catch specific
   exceptions when you have a concrete plan to handle them.
4. When instructed to "let errors bubble up," do NOT add try/except blocks.
5. NEVER catch a bare `Exception`. ONLY catch specific errors.
6. Do NOT allow for graceful degradation. The code path should succeed OR raise
   an error.

```python
# WRONG: Swallowing errors and continuing
for item in items:
    try:
        result = process_item(item)
        results.append(result)
    except ValueError:
        continue  # This hides the real problem

# RIGHT: Let errors bubble up to expose the issue
for item in items:
    result = process_item(item)  # Will fail fast if there's an issue
    results.append(result)
```

# Legibility

## Module layout

Keep `__init__.py` empty. Put module-level code in a file that matches the
package name, e.g. `foundation/database.py`.

Place public exports at the top of the file; private functions and helpers go at
the bottom.

## Docstrings

Do NOT write docstrings. The human programmer will write high-quality bespoke
docstrings once you are done with your work. **DO NOT WRITE DOCSTRINGS.**

## Imports

For standard library and third-party dependencies, import full modules rather
than individual functions unless the function name is unique or the import path
has three-or-more parts.

```python
# Prefer
import dataclasses
@dataclasses.dataclass(slots=True)

# Over
from dataclasses import dataclass
```

## Date Parsing

When parsing ISO dates, use `datetime.fromisoformat()` directly. Let parsing
errors bubble up instead of defaulting to fallback dates:

```python
# Bad: silently falling back to today's date
try:
    date = datetime.datetime.fromisoformat(date_str).date()
except (ValueError, AttributeError):
    date = datetime.date.today()

# Good: let the error bubble up to expose data quality issues
date = datetime.datetime.fromisoformat(date_str).date()
```

# Database

The database lives at `~/.local/share/lixue/knowledge.sqlite3`. Run
`scripts/database-migrate.py` to create and migrate it.

## Connection

Use the context manager `foundation.database.connect(db_path)` to get a
`sqlite3.Connection` with:

- `row_factory = sqlite3.Row` (dict-like row access)
- `PRAGMA foreign_keys=ON`
- `PRAGMA journal_mode=WAL`
- `isolation_level=None` (autocommit; use explicit `BEGIN`/`COMMIT`)

## Schema sources

- **`schema.sql`:** definitive schema snapshot. *Read, never edit.*
- **`migrations/`:** yoyo migration files. Source of truth for schema changes.

## Migrations

**CRITICAL: Before touching ANY database migration file, you MUST use the
`database-migration-creation` skill.** Do NOT create, modify, or delete
migration files without using this skill first.

Migrations live in `migrations/` and are plain SQL files managed by yoyo.

```bash
just new-migration "description"  # scaffold a new migration
just codegen-db                   # regenerate schema.sql and Python bindings
```

Create at most one migration per branch. If the current branch already has a
migration, update it in-place instead of adding a new one.

After writing or editing a migration, always regenerate:

```bash
just codegen-db
```

## Versioning scheme

All root entity tables are suffixed `_versioned` with `(id, version)` as the
composite primary key. A companion view exposes only the latest non-deleted row.
Use `BOOLEAN` for the `deleted` column so codegen produces `bool` in Python.

Junction tables are also versioned, but their version axis is the **parent
entity's version**. A junction row records which parent version introduced or
removed the association. Only rows where the association actually changed are
written (sparse versioning). A `deleted` flag marks removals.

To reconstruct a junction set at parent version N, for each associated entity
find the latest junction row with `parent_version <= N` and check `deleted = 0`.

## Queries

We use the sqlc ORM to write database queries. **All** queries are stored in
`queries.sql` files. Access the `database-query-writing` skill when
investigating or modifying the database queries. **Never write raw SQL in
Python code.** Even in tests.

```sql
-- name: idea_get_by_id :one
SELECT * FROM ideas WHERE id = ?;

-- name: idea_list :many
SELECT * FROM ideas ORDER BY name;

-- name: idea_create :execlastid
INSERT INTO ideas (name) VALUES (?);
```

Supported commands: `:exec`, `:execresult`, `:execlastid`, `:one`, `:many`.

Name queries as `{resource}_{action}_{filter}`. For example: `idea_create`,
`idea_get_by_id`, `idea_list_by_tag`.

Never directly modify anything in a `__codegen__` directory; they are generated
artifacts. To regenerate:

```bash
just codegen-db
```

# Testing

Treat tests as first-class citizens of the codebase. They are equal in
importance to the implementation. This means that:

1. We build useful abstractions for efficient and robust test writing.
2. We limit the tests to a small set of extremely high value tests.
3. We carefully choose each step and property under test to cover the desired
   behaviors.

Refer to the `python-test-writing` skill whenever you are writing a test.

- Place tests in `pkg/module_test.py` next to the implementation.
- Keep a flat hierarchy of test functions. Do not nest tests inside classes.
- Do NOT use mocks. Use fakes that imitate services in a logical, state-tracking
  way.
- Prefer to assert on complete objects instead of field-by-field assertions.
- You are NOT allowed to skip tests. If stuck, stop and ask the user.
- When a test times out, do NOT skip it. It is a MAJOR problem.

```bash
just test          # pytest with coverage (parallel)
just check         # test + lintcheck
```

Tests are named `*_test.py` and discovered by pytest. Config is in
`pyproject.toml`.

## Database in tests

- The `t.db_path` gives you a `Path` to a session-scoped migrated test
  database. Use `foundation.database.connect(t.db_path)` to get a connection.
- We share one database between all tests for performance.

# Scripts

Executable scripts live in `scripts/`. Each script is a standalone `chmod +x`
Python file with a `#!/usr/bin/env python3` shebang. Scripts should be
self-contained and import only from the standard library and dependencies
available in the Nix dev shell.
