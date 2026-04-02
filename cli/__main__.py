from __future__ import annotations

import dataclasses
import json
import sys

import click

from __codegen__.queries import (
    query_hierarchy_bump_version,
    query_hierarchy_create,
    query_hierarchy_delete,
    query_hierarchy_get_by_id,
    query_hierarchy_idea_add,
    query_hierarchy_idea_list,
    query_hierarchy_idea_remove,
    query_hierarchy_list,
    query_hierarchy_update,
    query_idea_bump_version,
    query_idea_create,
    query_idea_delete,
    query_idea_get_by_id,
    query_idea_get_by_name,
    query_idea_list,
    query_idea_tag_add,
    query_idea_tag_list,
    query_idea_tag_remove,
    query_idea_update,
    query_relationship_create,
    query_relationship_delete,
    query_relationship_get_by_id,
    query_relationship_list,
    query_relationship_list_by_from,
    query_relationship_list_by_involving,
    query_relationship_list_by_to,
    query_relationship_update,
    query_source_create,
    query_source_delete,
    query_source_get_by_id,
    query_source_get_by_slug,
    query_source_list,
    query_source_update,
    query_tag_create,
    query_tag_delete,
    query_tag_get_by_id,
    query_tag_list,
    query_tag_update,
)
from foundation.database import connect


@click.group()
def main() -> None:
    pass


# -- Ideas ---------------------------------------------------------------------


@main.group()
def idea() -> None:
    pass


@idea.command("list")
def idea_list_cmd() -> None:
    with connect() as conn:
        for row in query_idea_list(conn):
            _print_json(row)


@idea.command("get")
@click.argument("id", type=int, required=False, default=None)
@click.option("--name", type=str, default=None)
def idea_get_cmd(id: int | None, name: str | None) -> None:
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
def idea_create_cmd(name: str, contents: str | None, managed: bool) -> None:
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
def idea_delete_cmd(id: int) -> None:
    with connect() as conn:
        query_idea_delete(conn, id=id)


@idea.command("tags")
@click.argument("idea_id", type=int)
def idea_tags_cmd(idea_id: int) -> None:
    with connect() as conn:
        for tag_id in query_idea_tag_list(conn, idea_id=idea_id):
            click.echo(json.dumps({"tag_id": tag_id}))


@idea.command("tag-add")
@click.argument("idea_id", type=int)
@click.argument("tag_id", type=int)
def idea_tag_add_cmd(idea_id: int, tag_id: int) -> None:
    with connect() as conn:
        query_idea_bump_version(conn, id=idea_id)
        current = query_idea_get_by_id(conn, id=idea_id)
        query_idea_tag_add(conn, idea_id=idea_id, idea_version=current.version, tag_id=tag_id)


@idea.command("tag-remove")
@click.argument("idea_id", type=int)
@click.argument("tag_id", type=int)
def idea_tag_remove_cmd(idea_id: int, tag_id: int) -> None:
    with connect() as conn:
        query_idea_bump_version(conn, id=idea_id)
        current = query_idea_get_by_id(conn, id=idea_id)
        query_idea_tag_remove(conn, idea_id=idea_id, idea_version=current.version, tag_id=tag_id)


# -- Tags ----------------------------------------------------------------------


@main.group()
def tag() -> None:
    pass


@tag.command("list")
def tag_list_cmd() -> None:
    with connect() as conn:
        for row in query_tag_list(conn):
            _print_json(row)


@tag.command("get")
@click.argument("id", type=int)
def tag_get_cmd(id: int) -> None:
    with connect() as conn:
        row = query_tag_get_by_id(conn, id=id)
    _print_json(row)


@tag.command("create")
@click.option("--name", required=True, type=str)
def tag_create_cmd(name: str) -> None:
    with connect() as conn:
        new_id = query_tag_create(conn, name=name)
        row = query_tag_get_by_id(conn, id=new_id)
    _print_json(row)


@tag.command("update")
@click.argument("id", type=int)
@click.option("--name", required=True, type=str)
def tag_update_cmd(id: int, name: str) -> None:
    with connect() as conn:
        query_tag_update(conn, id=id, name=name)
        row = query_tag_get_by_id(conn, id=id)
    _print_json(row)


@tag.command("delete")
@click.argument("id", type=int)
def tag_delete_cmd(id: int) -> None:
    with connect() as conn:
        query_tag_delete(conn, id=id)


# -- Relationships -------------------------------------------------------------


@main.group()
def relationship() -> None:
    pass


@relationship.command("list")
@click.option("--from", "from_id", type=int, default=None)
@click.option("--to", "to_id", type=int, default=None)
@click.option("--involving", type=int, default=None)
def relationship_list_cmd(from_id: int | None, to_id: int | None, involving: int | None) -> None:
    with connect() as conn:
        if involving is not None:
            rows = query_relationship_list_by_involving(conn, from_idea_id=involving, to_idea_id=involving, underlying_idea_id=involving)
        elif from_id is not None:
            rows = query_relationship_list_by_from(conn, from_idea_id=from_id)
        elif to_id is not None:
            rows = query_relationship_list_by_to(conn, to_idea_id=to_id)
        else:
            rows = query_relationship_list(conn)
        for row in rows:
            _print_json(row)


@relationship.command("get")
@click.argument("id", type=int)
def relationship_get_cmd(id: int) -> None:
    with connect() as conn:
        row = query_relationship_get_by_id(conn, id=id)
    _print_json(row)


@relationship.command("create")
@click.option("--from", "from_id", required=True, type=int)
@click.option("--to", "to_id", required=True, type=int)
@click.option("--underlying", required=True, type=int)
@click.option("--kind", required=True, type=str)
@click.option("--metadata", "metadata_json", type=str, default=None)
def relationship_create_cmd(from_id: int, to_id: int, underlying: int, kind: str, metadata_json: str | None) -> None:
    with connect() as conn:
        new_id = query_relationship_create(
            conn,
            underlying_idea_id=underlying,
            kind=kind,
            metadata=metadata_json,
            from_idea_id=from_id,
            to_idea_id=to_id,
        )
        row = query_relationship_get_by_id(conn, id=new_id)
    _print_json(row)


@relationship.command("update")
@click.argument("id", type=int)
@click.option("--kind", type=str, default=None)
@click.option("--metadata", "metadata_json", type=str, default=None)
def relationship_update_cmd(id: int, kind: str | None, metadata_json: str | None) -> None:
    with connect() as conn:
        current = query_relationship_get_by_id(conn, id=id)
        query_relationship_update(
            conn,
            id=id,
            kind=kind if kind is not None else current.kind,
            metadata=metadata_json if metadata_json is not None else current.metadata,
        )
        row = query_relationship_get_by_id(conn, id=id)
    _print_json(row)


@relationship.command("delete")
@click.argument("id", type=int)
def relationship_delete_cmd(id: int) -> None:
    with connect() as conn:
        query_relationship_delete(conn, id=id)


# -- Sources -------------------------------------------------------------------


@main.group()
def source() -> None:
    pass


@source.command("list")
def source_list_cmd() -> None:
    with connect() as conn:
        for row in query_source_list(conn):
            _print_json(row)


@source.command("get")
@click.argument("id", type=int, required=False, default=None)
@click.option("--slug", type=str, default=None)
def source_get_cmd(id: int | None, slug: str | None) -> None:
    if id is None and slug is None:
        click.echo("error: must provide <id> or --slug", err=True)
        sys.exit(1)
    with connect() as conn:
        if id is not None:
            row = query_source_get_by_id(conn, id=id)
        else:
            assert slug is not None
            row = query_source_get_by_slug(conn, slug=slug)
    _print_json(row)


@source.command("create")
@click.option("--slug", required=True, type=str)
@click.option("--title", required=True, type=str)
@click.option("--authors", type=str, default="[]")
@click.option("--original-year", type=int, default=None)
@click.option("--circa", is_flag=True, default=False)
@click.option("--edition-year", type=int, default=None)
@click.option("--edition", type=str, default=None)
@click.option("--translators", type=str, default="[]")
@click.option("--publisher", type=str, default="")
def source_create_cmd(
    slug: str,
    title: str,
    authors: str,
    original_year: int | None,
    circa: bool,
    edition_year: int | None,
    edition: str | None,
    translators: str,
    publisher: str,
) -> None:
    with connect() as conn:
        idea_id = query_idea_create(conn, name=title, contents=None, managed=True)
        new_id = query_source_create(
            conn,
            underlying_idea_id=idea_id,
            slug=slug,
            meta_title=title,
            meta_authors=authors,
            meta_original_year=original_year,
            original_year_is_circa=circa or None,
            edition_year=edition_year,
            edition_year_is_circa=None,
            edition=edition,
            translators=translators,
            publisher=publisher,
        )
        row = query_source_get_by_id(conn, id=new_id)
    _print_json(row)


@source.command("update")
@click.argument("id", type=int)
@click.option("--slug", type=str, default=None)
@click.option("--title", type=str, default=None)
@click.option("--authors", type=str, default=None)
@click.option("--original-year", type=int, default=None)
@click.option("--circa", type=bool, default=None)
@click.option("--edition-year", type=int, default=None)
@click.option("--edition", type=str, default=None)
@click.option("--translators", type=str, default=None)
@click.option("--publisher", type=str, default=None)
@click.option("--fact-sheet", type=str, default=None)
def source_update_cmd(
    id: int,
    slug: str | None,
    title: str | None,
    authors: str | None,
    original_year: int | None,
    circa: bool | None,
    edition_year: int | None,
    edition: str | None,
    translators: str | None,
    publisher: str | None,
    fact_sheet: str | None,
) -> None:
    with connect() as conn:
        current = query_source_get_by_id(conn, id=id)
        query_source_update(
            conn,
            id=id,
            slug=slug if slug is not None else current.slug,
            fact_sheet=fact_sheet if fact_sheet is not None else current.fact_sheet,
            meta_title=title if title is not None else current.meta_title,
            meta_authors=authors if authors is not None else current.meta_authors,
            meta_original_year=original_year if original_year is not None else current.meta_original_year,
            original_year_is_circa=circa if circa is not None else current.original_year_is_circa,
            edition_year=edition_year if edition_year is not None else current.edition_year,
            edition_year_is_circa=current.edition_year_is_circa,
            edition=edition if edition is not None else current.edition,
            translators=translators if translators is not None else current.translators,
            publisher=publisher if publisher is not None else current.publisher,
        )
        row = query_source_get_by_id(conn, id=id)
    _print_json(row)


@source.command("delete")
@click.argument("id", type=int)
def source_delete_cmd(id: int) -> None:
    with connect() as conn:
        query_source_delete(conn, id=id)


# -- Hierarchies ---------------------------------------------------------------


@main.group()
def hierarchy() -> None:
    pass


@hierarchy.command("list")
def hierarchy_list_cmd() -> None:
    with connect() as conn:
        for row in query_hierarchy_list(conn):
            _print_json(row)


@hierarchy.command("get")
@click.argument("id", type=int)
def hierarchy_get_cmd(id: int) -> None:
    with connect() as conn:
        row = query_hierarchy_get_by_id(conn, id=id)
    _print_json(row)


@hierarchy.command("create")
@click.option("--name", required=True, type=str)
@click.option("--notes", type=str, default=None)
@click.option("--check-tags", type=str, default="[]")
def hierarchy_create_cmd(name: str, notes: str | None, check_tags: str) -> None:
    with connect() as conn:
        new_id = query_hierarchy_create(conn, name=name, notes=notes, check_tags=check_tags)
        row = query_hierarchy_get_by_id(conn, id=new_id)
    _print_json(row)


@hierarchy.command("update")
@click.argument("id", type=int)
@click.option("--name", type=str, default=None)
@click.option("--notes", type=str, default=None)
@click.option("--check-tags", type=str, default=None)
def hierarchy_update_cmd(id: int, name: str | None, notes: str | None, check_tags: str | None) -> None:
    with connect() as conn:
        current = query_hierarchy_get_by_id(conn, id=id)
        query_hierarchy_update(
            conn,
            id=id,
            name=name if name is not None else current.name,
            notes=notes if notes is not None else current.notes,
            check_tags=check_tags if check_tags is not None else current.check_tags,
        )
        row = query_hierarchy_get_by_id(conn, id=id)
    _print_json(row)


@hierarchy.command("delete")
@click.argument("id", type=int)
def hierarchy_delete_cmd(id: int) -> None:
    with connect() as conn:
        query_hierarchy_delete(conn, id=id)


@hierarchy.command("members")
@click.argument("hierarchy_id", type=int)
def hierarchy_members_cmd(hierarchy_id: int) -> None:
    with connect() as conn:
        for row in query_hierarchy_idea_list(conn, hierarchy_id=hierarchy_id):
            _print_json(row)


@hierarchy.command("member-add")
@click.argument("hierarchy_id", type=int)
@click.argument("idea_id", type=int)
@click.option("--parent", type=int, default=None)
@click.option("--relationship", type=int, default=None)
def hierarchy_member_add_cmd(hierarchy_id: int, idea_id: int, parent: int | None, relationship: int | None) -> None:
    with connect() as conn:
        query_hierarchy_bump_version(conn, id=hierarchy_id)
        current = query_hierarchy_get_by_id(conn, id=hierarchy_id)
        query_hierarchy_idea_add(
            conn,
            hierarchy_id=hierarchy_id,
            hierarchy_version=current.version,
            idea_id=idea_id,
            parent_idea_id=parent,
            relationship_id=relationship,
        )


@hierarchy.command("member-remove")
@click.argument("hierarchy_id", type=int)
@click.argument("idea_id", type=int)
def hierarchy_member_remove_cmd(hierarchy_id: int, idea_id: int) -> None:
    with connect() as conn:
        query_hierarchy_bump_version(conn, id=hierarchy_id)
        current = query_hierarchy_get_by_id(conn, id=hierarchy_id)
        query_hierarchy_idea_remove(conn, hierarchy_id=hierarchy_id, hierarchy_version=current.version, idea_id=idea_id)


# -- Private helpers -----------------------------------------------------------


_BOOL_FIELDS = {"managed", "deleted", "original_year_is_circa", "edition_year_is_circa"}


def _print_json(obj: object) -> None:
    d = dataclasses.asdict(obj)
    for key in _BOOL_FIELDS:
        if key in d and d[key] is not None:
            d[key] = bool(d[key])
    click.echo(json.dumps(d))


if __name__ == "__main__":
    main()
