import sys

import click

from lixue_cards.cli import cli


def main() -> None:
    try:
        cli()
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main()
