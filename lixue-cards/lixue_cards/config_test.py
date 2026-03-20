from pathlib import Path

import pytest

from lixue_cards.config import anki_data_dir, collection_path


def test_collection_path_default() -> None:
    path = collection_path("User 1")
    assert path.name == "collection.anki2"
    assert "User 1" in str(path)


def test_anki_data_dir_respects_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANKI_DATA", "/tmp/test-anki")
    assert anki_data_dir() == Path("/tmp/test-anki")


def test_anki_data_dir_respects_xdg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANKI_DATA", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", "/tmp/xdg-data")
    assert anki_data_dir() == Path("/tmp/xdg-data/Anki2")
