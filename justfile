lint *ARGS:  ## Auto-fix: ruff format + ruff check --fix.
    ruff format {{ARGS}}
    ruff check --fix {{ARGS}}

lintcheck *ARGS:  ## Check linting without fixing.
    ruff format --check {{ARGS}}
    ruff check {{ARGS}}

migrate:  ## Create/migrate the knowledge database.
    scripts/database-migrate.py
