"""CLI interface for lixue-cards."""

from __future__ import annotations

from pathlib import Path

import click

from lixue_cards.notes import add_basic_note, add_cloze_note


@click.group()
def cli() -> None:
    """lixue-cards: Anki card management tools."""


@cli.command()
def version() -> None:
    """Print the version."""
    version_file = Path(__file__).parent / ".version"
    click.echo(version_file.read_text().strip())


@cli.command()
@click.option("--front", "-f", required=True, help="Front (question) of the card.")
@click.option("--back", "-b", required=True, help="Back (answer) of the card.")
@click.option("--citation", "-c", default="", help="Citation/source for the card.")
@click.option("--tag", "-t", multiple=True, help="Tags (can be specified multiple times).")
@click.option("--deck", "-d", default="Default", help="Deck name.")
@click.option("--profile", "-p", default="User 1", help="Anki profile name.")
def basic(
    front: str,
    back: str,
    citation: str,
    tag: tuple[str, ...],
    deck: str,
    profile: str,
) -> None:
    """Add a Basic note (Front/Back/Citation)."""
    note_id = add_basic_note(
        front=front,
        back=back,
        citation=citation,
        tags=list(tag) if tag else None,
        deck=deck,
        profile=profile,
    )
    click.echo(f"Created Basic note {note_id}")


@cli.command()
@click.option("--text", "-x", required=True, help="Cloze text with deletions (e.g. '{{c1::answer}}').")
@click.option("--citation", "-c", default="", help="Citation/source for the card.")
@click.option("--tag", "-t", multiple=True, help="Tags (can be specified multiple times).")
@click.option("--deck", "-d", default="Default", help="Deck name.")
@click.option("--profile", "-p", default="User 1", help="Anki profile name.")
def cloze(
    text: str,
    citation: str,
    tag: tuple[str, ...],
    deck: str,
    profile: str,
) -> None:
    """Add a Cloze note (Text/Citation)."""
    note_id = add_cloze_note(
        text=text,
        citation=citation,
        tags=list(tag) if tag else None,
        deck=deck,
        profile=profile,
    )
    click.echo(f"Created Cloze note {note_id}")
