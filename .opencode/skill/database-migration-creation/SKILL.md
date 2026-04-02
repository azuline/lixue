---
name: database-migration-creation
description: How to create and manage database migrations. Use it before starting to write a database migration.
---

# Database Migration Creation

Use this sequence of commands when creating a database migration:

```bash
just new-migration <name>  # scaffold
just codegen-db            # regenerate schema.sql and Python bindings
```

## Migration rules

- NEVER CREATE A MIGRATION FILE BY HAND, ALWAYS USE `JUST NEW-MIGRATION`.
- Never modify the `-- depends:` header in migration files.
- Never change a migration from another branch.
- We do **not** support down-migrations.
- After writing or editing a migration, always run `just codegen-db` to
  regenerate `schema.sql` and the Python bindings.
- To inspect the current schema, run `just codegen-db` and then read
  `schema.sql`.
- Create at most one migration per branch. Before creating a new migration with
  `just new-migration`, check if the current branch already has a migration. If
  so, update that migration in-place instead of adding a new one.

## Column conventions

- Use `INTEGER` for IDs (SQLite autoincrement).
- Use `TEXT` for strings, dates (ISO 8601), and JSON arrays (serialized as JSON
  text).
- Use `BOOLEAN` for boolean fields (codegen produces `bool` in Python).
- Foreign keys reference the `_versioned` table's `id` column (not the view).

Express enums as enum tables:

```sql
CREATE TABLE new_kind_enum (value TEXT PRIMARY KEY NOT NULL);
INSERT INTO new_kind_enum (value) VALUES ('value1'), ('value2');
-- Usage: some_column TEXT NOT NULL REFERENCES new_kind_enum(value)
```

## Versioned root entity tables

Root entity tables are suffixed `_versioned` and store every version of a row.
Views on top present the latest non-deleted data. Each versioned table has:

- `id INTEGER NOT NULL`
- `version INTEGER NOT NULL`
- `inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))`
- `updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))`
- `deleted BOOLEAN NOT NULL DEFAULT 0`
- `PRIMARY KEY (id, version)`

```sql
CREATE TABLE new_things_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    -- entity fields here --
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted BOOLEAN NOT NULL DEFAULT 0,
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

## Versioned junction tables

Junction tables are versioned on the **parent entity's version axis**. They do
NOT have their own independent version counter. Only rows where the association
actually changed are written (sparse versioning).

- The primary key is `(parent_id, parent_version, child_id)`.
- `parent_version` references the parent entity's `(id, version)` composite FK.
- `deleted BOOLEAN NOT NULL DEFAULT 0` marks removals.
- `inserted_at` records when the junction row was written.
- No `updated_at` (junction rows are immutable once written; a new parent
  version is created instead).

```sql
CREATE TABLE parent_children (
    parent_id INTEGER NOT NULL,
    parent_version INTEGER NOT NULL,
    child_id INTEGER NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (parent_id, parent_version, child_id),
    FOREIGN KEY (parent_id, parent_version) REFERENCES parents_versioned(id, version),
    FOREIGN KEY (child_id) REFERENCES children_versioned(id)
);
```

### Write pattern

Only write junction rows when the association set changes. When the parent is
updated but its associations are unchanged, write nothing to the junction table.

- **Adding** child C at parent version 3: insert `(parent_id, 3, C, deleted=0)`.
- **Removing** child C at parent version 4: insert `(parent_id, 4, C, deleted=1)`.
- **Unchanged** associations at parent version 5: write nothing.

### Read pattern (snapshot at parent version N)

```sql
SELECT child_id
FROM parent_children jt
INNER JOIN (
    SELECT child_id, MAX(parent_version) AS max_version
    FROM parent_children
    WHERE parent_id = ? AND parent_version <= ?
    GROUP BY child_id
) latest ON jt.child_id = latest.child_id AND jt.parent_version = latest.max_version
WHERE jt.parent_id = ? AND jt.deleted = 0;
```
