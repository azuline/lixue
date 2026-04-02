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
  `idea_get_by_id`, `idea_list_by_tag`.
- Never directly modify anything in a `__codegen__` directory; they are
  generated artifacts.

## Supported commands

- `:exec` -- execute a statement, return nothing.
- `:execresult` -- execute a statement, return `sqlite3.Cursor`.
- `:execlastid` -- execute an INSERT, return `int` (last row ID).
- `:one` -- fetch exactly one row. Raises `ValueError` if none found.
- `:many` -- fetch all rows as an iterator.

## Versioned root entity queries

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

## Versioned junction queries

Junction tables are versioned on the parent entity's version axis. Only write
junction rows when the association set actually changes (sparse versioning).

### Writing junction changes

When adding or removing associations, write rows tied to the new parent version:

```sql
-- name: idea_tag_add :exec
INSERT INTO idea_tags (idea_id, idea_version, tag_id, deleted)
VALUES (?, ?, ?, 0);

-- name: idea_tag_remove :exec
INSERT INTO idea_tags (idea_id, idea_version, tag_id, deleted)
VALUES (?, ?, ?, 1);
```

### Reading current junction state

To get the current associations for the latest version of a parent entity:

```sql
-- name: idea_tag_list :many
SELECT jt.tag_id
FROM idea_tags jt
INNER JOIN (
    SELECT tag_id, MAX(idea_version) AS max_version
    FROM idea_tags
    WHERE idea_id = ?
    GROUP BY tag_id
) latest ON jt.tag_id = latest.tag_id AND jt.idea_version = latest.max_version
WHERE jt.idea_id = ? AND jt.deleted = 0;
```

### Reading junction state at a specific parent version

```sql
-- name: idea_tag_list_at_version :many
SELECT jt.tag_id
FROM idea_tags jt
INNER JOIN (
    SELECT tag_id, MAX(idea_version) AS max_version
    FROM idea_tags
    WHERE idea_id = ? AND idea_version <= ?
    GROUP BY tag_id
) latest ON jt.tag_id = latest.tag_id AND jt.idea_version = latest.max_version
WHERE jt.idea_id = ? AND jt.deleted = 0;
```
