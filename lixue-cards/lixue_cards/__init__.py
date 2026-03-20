"""lixue-cards: Anki card management tools."""

from lixue_cards.config import anki_data_dir, collection_path
from lixue_cards.notes import (
    DeckNotFoundError,
    InvalidClozeError,
    LixueCardsError,
    NotetypeNotFoundError,
    add_basic_note,
    add_cloze_note,
)

__all__ = [
    # Errors
    "DeckNotFoundError",
    "InvalidClozeError",
    "LixueCardsError",
    "NotetypeNotFoundError",
    # Note creation
    "add_basic_note",
    "add_cloze_note",
    # Config
    "anki_data_dir",
    "collection_path",
]
