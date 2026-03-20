"""Configuration and path resolution for lixue-cards."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_ANKI_PROFILE = "User 1"


def anki_data_dir() -> Path:
    """Return the Anki data directory.

    Respects the ANKI_DATA environment variable if set, otherwise uses the
    platform default (~/.local/share/Anki2 on Linux).
    """
    env = os.environ.get("ANKI_DATA")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "Anki2"
    return Path.home() / ".local" / "share" / "Anki2"


def collection_path(profile: str = DEFAULT_ANKI_PROFILE) -> Path:
    """Return the path to an Anki profile's collection database."""
    return anki_data_dir() / profile / "collection.anki2"
