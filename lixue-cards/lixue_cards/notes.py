"""Library functions for creating Anki notes.

This module provides functions for adding Basic and Cloze notes to a local
Anki collection. Anki must be closed when using these functions, as they
open the SQLite database directly via Anki's backend.
"""

from __future__ import annotations

import re
from pathlib import Path

from anki.collection import Collection
from anki.decks import DeckId
from anki.notes import NoteId

from lixue_cards.config import collection_path


class LixueCardsError(Exception):
    """Base exception for lixue-cards errors."""


class NotetypeNotFoundError(LixueCardsError):
    """Raised when a notetype is not found in the collection."""


class DeckNotFoundError(LixueCardsError):
    """Raised when a deck is not found in the collection."""


class InvalidClozeError(LixueCardsError):
    """Raised when cloze text does not contain any cloze deletions."""


def _open_collection(profile: str) -> Collection:
    """Open an Anki collection for the given profile."""
    path = collection_path(profile)
    if not path.exists():
        raise LixueCardsError(f"Collection not found: {path}")
    return Collection(str(path))


def _resolve_deck_id(col: Collection, deck: str) -> DeckId:
    """Resolve a deck name to its ID, raising if not found."""
    deck_id = col.decks.id_for_name(deck)
    if deck_id is None:
        raise DeckNotFoundError(f"Deck not found: {deck!r}")
    return deck_id


def _get_notetype(col: Collection, name: str) -> dict:  # type: ignore[type-arg]
    """Look up a notetype by name, raising if not found."""
    notetype = col.models.by_name(name)
    if notetype is None:
        raise NotetypeNotFoundError(f"Notetype not found: {name!r}")
    return notetype


def add_basic_note(
    *,
    front: str,
    back: str,
    citation: str = "",
    tags: list[str] | None = None,
    deck: str = "Default",
    profile: str = "User 1",
) -> NoteId:
    """Add a Basic note to the Anki collection.

    Args:
        front: The front (question) field.
        back: The back (answer) field.
        citation: Optional citation/source field.
        tags: Optional list of tags.
        deck: Name of the deck to add the note to.
        profile: Anki profile name.

    Returns:
        The ID of the newly created note.

    Raises:
        LixueCardsError: If the collection cannot be opened.
        NotetypeNotFoundError: If the "Basic" notetype is not found.
        DeckNotFoundError: If the specified deck is not found.
    """
    col = _open_collection(profile)
    try:
        notetype = _get_notetype(col, "Basic")
        deck_id = _resolve_deck_id(col, deck)

        note = col.new_note(notetype)
        note["Front"] = front
        note["Back"] = back
        if "Citation" in note:
            note["Citation"] = citation
        if tags:
            note.tags = tags

        col.add_note(note, deck_id)
        return note.id
    finally:
        col.close()


def add_cloze_note(
    *,
    text: str,
    citation: str = "",
    tags: list[str] | None = None,
    deck: str = "Default",
    profile: str = "User 1",
) -> NoteId:
    """Add a Cloze note to the Anki collection.

    The text must contain at least one cloze deletion in the form
    ``{{c1::answer}}`` or ``{{c1::answer::hint}}``.

    Args:
        text: The cloze text with deletions (e.g. ``"{{c1::Paris}} is the capital of France"``).
        citation: Optional citation/source field.
        tags: Optional list of tags.
        deck: Name of the deck to add the note to.
        profile: Anki profile name.

    Returns:
        The ID of the newly created note.

    Raises:
        InvalidClozeError: If the text contains no cloze deletions.
        LixueCardsError: If the collection cannot be opened.
        NotetypeNotFoundError: If the "Cloze" notetype is not found.
        DeckNotFoundError: If the specified deck is not found.
    """
    if not re.search(r"\{\{c\d+::", text):
        raise InvalidClozeError("Cloze text must contain at least one cloze deletion (e.g. {{c1::answer}})")

    col = _open_collection(profile)
    try:
        notetype = _get_notetype(col, "Cloze")
        deck_id = _resolve_deck_id(col, deck)

        note = col.new_note(notetype)
        note["Text"] = text
        if "Citation" in note:
            note["Citation"] = citation
        if tags:
            note.tags = tags

        col.add_note(note, deck_id)
        return note.id
    finally:
        col.close()
