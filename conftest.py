from __future__ import annotations

import dataclasses
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

from database.connection import connect, migrate


@dataclasses.dataclass(slots=True)
class LixueFixture:
    db_path: Path

    @classmethod
    def create(cls, db_path: Path) -> LixueFixture:
        return cls(db_path=db_path)


@pytest.fixture(scope="session")
def _test_db_path() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        migrate(db_path)
        yield db_path


@pytest.fixture
def t(_test_db_path: Path) -> LixueFixture:
    return LixueFixture.create(db_path=_test_db_path)
