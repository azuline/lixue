"""Entry point for lixue-cards CLI."""

from __future__ import annotations

import sys

import click

from lixue_cards.cli import cli
from lixue_cards.notes import LixueCardsError


def main() -> None:
    try:
        cli()
    except LixueCardsError as e:
        click.secho(f"{e.__class__.__name__}: {e}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
