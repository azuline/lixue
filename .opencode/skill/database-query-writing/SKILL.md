---
name: database-query-writing
description: How to write database queries using the sqlc ORM. Use it when investigating or modifying database queries.
---

# Database Query Writing

Write SQL queries in `queries.sql` files using sqlc annotations. After editing
any `queries.sql`, regenerate the ORM with:

```bash
just codegen-db
```

Access the generated query functions by importing from the codegen package and
passing a `sqlite3.Connection`:

```python
from __codegen__.queries import query_idea_get_by_id
from foundation.database import connect

with connect(db_path) as conn:
    idea = query_idea_get_by_id(conn, id=42)
```

## Conventions

- Never use raw SQL in Python. Always use the sqlc ORM. Even in tests.
- Never set `inserted_at` or `updated_at` in code; database defaults handle
  them.
- Name queries as `{resource}_{action}_{filter}`. For example: `idea_create`,
  `idea_get_by_id`, `idea_list_by_discipline`.
- Never directly modify anything in a `__codegen__` directory; they are
  generated artifacts.

## Supported commands

- `:exec` -- execute a statement, return nothing.
- `:execresult` -- execute a statement, return `sqlite3.Cursor`.
- `:execlastid` -- execute an INSERT, return `int` (last row ID).
- `:one` -- fetch exactly one row. Raises `ValueError` if none found.
- `:many` -- fetch all rows as an iterator.

## Versioned table queries

When inserting into versioned tables, use this pattern to generate the next ID:

```sql
-- name: thing_create :execlastid
INSERT INTO things_versioned (id, version, name)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM things_versioned), 1, ?);
```

When querying, select from the **view** (not the `_versioned` table) to get
latest non-deleted rows:

```sql
-- name: thing_get_by_id :one
SELECT * FROM things WHERE id = ?;

-- name: thing_list :many
SELECT * FROM things ORDER BY name;
```
