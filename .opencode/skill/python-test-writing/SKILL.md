---
name: python-test-writing
description: How to write Python tests following project conventions. Use it whenever writing a test.
---

# Python Test Writing

## Conventions

- Tests are MORE important than the implementation. Give them the corresponding
  care.
- Place a test for `pkg/module.py` in `pkg/module_test.py`.
- Do not create a second test file `module_{something}_test.py` for `module.py`.
- Keep a flat test hierarchy of functions. Do not nest tests inside classes.
- Do not preserve unused functions post-refactor just for tests. Migrate the
  tests to the latest code implementation.

## Setup

- We have all our fixtures available as objects and methods on a `t` pytest
  fixture. See `conftest.py` for the `LixueFixture` definition.
- If no fixtures are needed, update the test function to take no parameter. Do
  not rename the fixture to `_t`.
- We do NOT use mocks. Instead, we use fakes that imitate the service in a
  logical and state-tracking way.

### Database

- The `t.db_path` gives a `Path` to a session-scoped migrated test database.
  Use `foundation.database.connect(t.db_path)` to get a connection.
- We share one database between all tests for performance.

## Assertions

- Prefer to assert on complete objects (GOOD) instead of doing
  line-by-line/field-by-field asserts (BAD). Those are very difficult to read.
- When a test times out, do NOT skip it. It is a MAJOR problem and you should
  pause and ask the user to help investigate.

## Skipping

- You are NOT allowed to skip tests. If you are stuck and cannot fix a broken
  test, stop and let the user know.
