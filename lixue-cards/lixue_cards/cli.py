import click


@click.group()
def cli() -> None:
    """lixue-cards: A card management tool."""


@cli.command()
def version() -> None:
    """Print the version."""
    from pathlib import Path

    version_file = Path(__file__).parent / ".version"
    click.echo(version_file.read_text().strip())
