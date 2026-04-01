# HELP

help:  ## Describe the available commands.
    @grep -E '^[a-z][^:]+:.*?## .*$$' justfile | sed 's/^/just /' | sed 's/ \*ARGS:/:/'

# CODE CHECKS

check: test lintcheck  ## Run all checks: test + lintcheck.

test *ARGS:  ## Run the test suite in parallel. Pass filename(s) like `just test file.py [file2.py::test_name]`.
    #!/usr/bin/env bash
    HALF_CORES=$(( $(nproc) / 2 ))
    [[ $HALF_CORES -lt 1 ]] && HALF_CORES=1
    pytest -n "$HALF_CORES" --dist worksteal {{ARGS}}

test-seq *ARGS:  ## Run the test suite sequentially.
    pytest {{ARGS}}

lintcheck *ARGS:  ## Check linting without fixing.
    ruff format --check {{ARGS}}
    ruff check {{ARGS}}

lint *ARGS:  ## Auto-fix: ruff format + ruff check --fix.
    ruff format {{ARGS}}
    ruff check --fix {{ARGS}}

# DATABASE

migrate:  ## Create/migrate the knowledge database.
    scripts/database-migrate.py

new-migration MSG:  ## Create a new migration file. ALWAYS use this to create a new migration.
    yoyo new --sql --message "{{MSG}}" migrations/

# CODEGEN

codegen-db:  ## Regenerate sqlc Python bindings and schema.sql from migrations.
    python -m tools.codegen_db
