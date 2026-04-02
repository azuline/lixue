from __future__ import annotations

import dataclasses
import warnings
from pathlib import Path

import pytest

warnings.filterwarnings("ignore", category=UserWarning, module="yoyo")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="yoyo")
warnings.filterwarnings("ignore", category=ResourceWarning)

import foundation.database  # noqa: E402


@dataclasses.dataclass(slots=True)
class LixueFixture:
    pass


@pytest.fixture(scope="session", autouse=True)
def _test_db(tmp_path_factory: pytest.TempPathFactory) -> Path:
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    foundation.database.migrate(db_path)
    foundation.database.DATABASE_PATH = db_path
    return db_path


@pytest.fixture
def t() -> LixueFixture:
    return LixueFixture()
