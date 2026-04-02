from __future__ import annotations

import dataclasses
import json
import sys

import click

from __codegen__.queries import (
    query_idea_create,
    query_idea_delete,
    query_idea_get_by_id,
    query_idea_get_by_name,
    query_idea_list,
    query_idea_update,
)
from foundation.database import connect


@click.group()
def main() -> None:
    pass


@main.group()
def idea() -> None:
    pass


@idea.command("list")
def idea_list() -> None:
    with connect() as conn:
        for row in query_idea_list(conn):
            _print_json(row)


@idea.command("get")
@click.argument("id", type=int, required=False, default=None)
@click.option("--name", type=str, default=None)
def idea_get(id: int | None, name: str | None) -> None:
    if id is None and name is None:
        click.echo("error: must provide <id> or --name", err=True)
        sys.exit(1)
    with connect() as conn:
        if id is not None:
            row = query_idea_get_by_id(conn, id=id)
        else:
            assert name is not None
            row = query_idea_get_by_name(conn, name=name)
    _print_json(row)


@idea.command("create")
@click.option("--name", required=True, type=str)
@click.option("--contents", type=str, default=None)
@click.option("--managed", is_flag=True, default=False)
def idea_create(name: str, contents: str | None, managed: bool) -> None:
    with connect() as conn:
        new_id = query_idea_create(conn, name=name, contents=contents, managed=managed)
        row = query_idea_get_by_id(conn, id=new_id)
    _print_json(row)


@idea.command("update")
@click.argument("id", type=int)
@click.option("--name", type=str, default=None)
@click.option("--contents", type=str, default=None)
@click.option("--managed", type=bool, default=None)
def idea_update_cmd(id: int, name: str | None, contents: str | None, managed: bool | None) -> None:
    with connect() as conn:
        current = query_idea_get_by_id(conn, id=id)
        query_idea_update(
            conn,
            id=id,
            name=name if name is not None else current.name,
            contents=contents if contents is not None else current.contents,
            managed=managed if managed is not None else current.managed,
        )
        row = query_idea_get_by_id(conn, id=id)
    _print_json(row)


@idea.command("delete")
@click.argument("id", type=int)
def idea_delete(id: int) -> None:
    with connect() as conn:
        query_idea_delete(conn, id=id)


# -- Private helpers -----------------------------------------------------------


_BOOL_FIELDS = {"managed", "deleted"}


def _print_json(obj: object) -> None:
    d = dataclasses.asdict(obj)
    for key in _BOOL_FIELDS:
        if key in d:
            d[key] = bool(d[key])
    click.echo(json.dumps(d))


if __name__ == "__main__":
    main()
