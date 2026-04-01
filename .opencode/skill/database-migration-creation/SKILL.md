---
name: database-migration-creation
description: How to create and manage database migrations. Use it before starting to write a database migration.
---

# Database Migration Creation

After writing or editing a migration, always run the migration script to verify:

```bash
scripts/database-migrate.py
```

## Migration rules

- Migrations live in `migrations/` as Python files using `yoyo.step()`.
- Create at most one migration per branch. If the current branch already has a
  migration, update it in-place instead of adding a new one.

## Versioned table conventions

Root entity tables use the versioning scheme. Follow this template:

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
