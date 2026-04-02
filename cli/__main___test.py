from __future__ import annotations

import json

from click.testing import CliRunner

from cli.__main__ import main


def _invoke(runner: CliRunner, args: list[str]) -> dict:
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    return json.loads(result.output.strip().splitlines()[-1])


def _invoke_lines(runner: CliRunner, args: list[str]) -> list[dict]:
    result = runner.invoke(main, args)
    assert result.exit_code == 0, result.output
    return [json.loads(line) for line in result.output.strip().splitlines()] if result.output.strip() else []


# -- Ideas ---------------------------------------------------------------------


def test_idea_crud() -> None:
    runner = CliRunner()

    created = _invoke(runner, ["idea", "create", "--name", "test idea", "--contents", "some content"])
    assert created["name"] == "test idea"
    assert created["contents"] == "some content"
    assert created["managed"] is False
    assert created["version"] == 1
    idea_id = created["id"]

    fetched = _invoke(runner, ["idea", "get", str(idea_id)])
    assert fetched["id"] == idea_id

    fetched_by_name = _invoke(runner, ["idea", "get", "--name", "test idea"])
    assert fetched_by_name["id"] == idea_id

    ideas = _invoke_lines(runner, ["idea", "list"])
    assert any(i["id"] == idea_id for i in ideas)

    updated = _invoke(runner, ["idea", "update", str(idea_id), "--name", "updated idea"])
    assert updated["name"] == "updated idea"
    assert updated["contents"] == "some content"
    assert updated["version"] == 2

    result = runner.invoke(main, ["idea", "delete", str(idea_id)])
    assert result.exit_code == 0

    result = runner.invoke(main, ["idea", "get", str(idea_id)])
    assert result.exit_code != 0


def test_idea_create_managed() -> None:
    runner = CliRunner()
    created = _invoke(runner, ["idea", "create", "--name", "managed idea", "--managed"])
    assert created["managed"] is True


def test_idea_get_requires_id_or_name() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["idea", "get"])
    assert result.exit_code != 0


# -- Tags ----------------------------------------------------------------------


def test_tag_crud() -> None:
    runner = CliRunner()

    created = _invoke(runner, ["tag", "create", "--name", "testtag"])
    assert created["name"] == "testtag"
    assert created["version"] == 1
    tag_id = created["id"]

    fetched = _invoke(runner, ["tag", "get", str(tag_id)])
    assert fetched["id"] == tag_id

    tags = _invoke_lines(runner, ["tag", "list"])
    assert any(t["id"] == tag_id for t in tags)

    updated = _invoke(runner, ["tag", "update", str(tag_id), "--name", "renamed"])
    assert updated["name"] == "renamed"
    assert updated["version"] == 2

    result = runner.invoke(main, ["tag", "delete", str(tag_id)])
    assert result.exit_code == 0

    result = runner.invoke(main, ["tag", "get", str(tag_id)])
    assert result.exit_code != 0


# -- Idea-Tag junction ---------------------------------------------------------


def test_idea_tag_add_remove() -> None:
    runner = CliRunner()

    idea = _invoke(runner, ["idea", "create", "--name", "taggable idea"])
    tag1 = _invoke(runner, ["tag", "create", "--name", "tag-a"])
    tag2 = _invoke(runner, ["tag", "create", "--name", "tag-b"])

    result = runner.invoke(main, ["idea", "tag-add", str(idea["id"]), str(tag1["id"])])
    assert result.exit_code == 0

    result = runner.invoke(main, ["idea", "tag-add", str(idea["id"]), str(tag2["id"])])
    assert result.exit_code == 0

    tag_rows = _invoke_lines(runner, ["idea", "tags", str(idea["id"])])
    tag_ids = {r["tag_id"] for r in tag_rows}
    assert tag_ids == {tag1["id"], tag2["id"]}

    result = runner.invoke(main, ["idea", "tag-remove", str(idea["id"]), str(tag1["id"])])
    assert result.exit_code == 0

    tag_rows = _invoke_lines(runner, ["idea", "tags", str(idea["id"])])
    tag_ids = {r["tag_id"] for r in tag_rows}
    assert tag_ids == {tag2["id"]}


# -- Relationships -------------------------------------------------------------


def test_relationship_crud() -> None:
    runner = CliRunner()

    idea_a = _invoke(runner, ["idea", "create", "--name", "rel idea a"])
    idea_b = _invoke(runner, ["idea", "create", "--name", "rel idea b"])
    idea_u = _invoke(runner, ["idea", "create", "--name", "rel underlying"])

    created = _invoke(
        runner,
        [
            "relationship",
            "create",
            "--from",
            str(idea_a["id"]),
            "--to",
            str(idea_b["id"]),
            "--underlying",
            str(idea_u["id"]),
            "--kind",
            "property",
        ],
    )
    assert created["kind"] == "property"
    assert created["from_idea_id"] == idea_a["id"]
    assert created["to_idea_id"] == idea_b["id"]
    rel_id = created["id"]

    fetched = _invoke(runner, ["relationship", "get", str(rel_id)])
    assert fetched["id"] == rel_id

    rels = _invoke_lines(runner, ["relationship", "list"])
    assert any(r["id"] == rel_id for r in rels)

    rels_from = _invoke_lines(runner, ["relationship", "list", "--from", str(idea_a["id"])])
    assert any(r["id"] == rel_id for r in rels_from)

    rels_involving = _invoke_lines(runner, ["relationship", "list", "--involving", str(idea_u["id"])])
    assert any(r["id"] == rel_id for r in rels_involving)

    updated = _invoke(runner, ["relationship", "update", str(rel_id), "--kind", "enumeration"])
    assert updated["kind"] == "enumeration"

    result = runner.invoke(main, ["relationship", "delete", str(rel_id)])
    assert result.exit_code == 0

    result = runner.invoke(main, ["relationship", "get", str(rel_id)])
    assert result.exit_code != 0


# -- Sources -------------------------------------------------------------------


def test_source_crud() -> None:
    runner = CliRunner()

    created = _invoke(
        runner,
        [
            "source",
            "create",
            "--slug",
            "test-source",
            "--title",
            "Test Source Title",
            "--authors",
            '["Author One"]',
            "--original-year",
            "1900",
        ],
    )
    assert created["slug"] == "test-source"
    assert created["meta_title"] == "Test Source Title"
    assert created["underlying_idea_id"] is not None
    source_id = created["id"]

    # Verify the auto-created underlying idea is managed.
    underlying = _invoke(runner, ["idea", "get", str(created["underlying_idea_id"])])
    assert underlying["managed"] is True
    assert underlying["name"] == "Test Source Title"

    fetched = _invoke(runner, ["source", "get", str(source_id)])
    assert fetched["id"] == source_id

    fetched_by_slug = _invoke(runner, ["source", "get", "--slug", "test-source"])
    assert fetched_by_slug["id"] == source_id

    sources = _invoke_lines(runner, ["source", "list"])
    assert any(s["id"] == source_id for s in sources)

    updated = _invoke(runner, ["source", "update", str(source_id), "--fact-sheet", "some notes"])
    assert updated["fact_sheet"] == "some notes"
    assert updated["meta_title"] == "Test Source Title"

    result = runner.invoke(main, ["source", "delete", str(source_id)])
    assert result.exit_code == 0

    result = runner.invoke(main, ["source", "get", str(source_id)])
    assert result.exit_code != 0


# -- Hierarchies ---------------------------------------------------------------


def test_hierarchy_crud() -> None:
    runner = CliRunner()

    created = _invoke(runner, ["hierarchy", "create", "--name", "test hierarchy"])
    assert created["name"] == "test hierarchy"
    assert created["version"] == 1
    h_id = created["id"]

    fetched = _invoke(runner, ["hierarchy", "get", str(h_id)])
    assert fetched["id"] == h_id

    hierarchies = _invoke_lines(runner, ["hierarchy", "list"])
    assert any(h["id"] == h_id for h in hierarchies)

    updated = _invoke(runner, ["hierarchy", "update", str(h_id), "--name", "renamed hierarchy"])
    assert updated["name"] == "renamed hierarchy"

    result = runner.invoke(main, ["hierarchy", "delete", str(h_id)])
    assert result.exit_code == 0

    result = runner.invoke(main, ["hierarchy", "get", str(h_id)])
    assert result.exit_code != 0


# -- Hierarchy members ---------------------------------------------------------


def test_hierarchy_member_add_remove() -> None:
    runner = CliRunner()

    h = _invoke(runner, ["hierarchy", "create", "--name", "member hierarchy"])
    idea_a = _invoke(runner, ["idea", "create", "--name", "member idea a"])
    idea_b = _invoke(runner, ["idea", "create", "--name", "member idea b"])

    result = runner.invoke(main, ["hierarchy", "member-add", str(h["id"]), str(idea_a["id"])])
    assert result.exit_code == 0

    result = runner.invoke(main, ["hierarchy", "member-add", str(h["id"]), str(idea_b["id"]), "--parent", str(idea_a["id"])])
    assert result.exit_code == 0

    members = _invoke_lines(runner, ["hierarchy", "members", str(h["id"])])
    member_ids = {m["idea_id"] for m in members}
    assert member_ids == {idea_a["id"], idea_b["id"]}

    child = next(m for m in members if m["idea_id"] == idea_b["id"])
    assert child["parent_idea_id"] == idea_a["id"]

    result = runner.invoke(main, ["hierarchy", "member-remove", str(h["id"]), str(idea_b["id"])])
    assert result.exit_code == 0

    members = _invoke_lines(runner, ["hierarchy", "members", str(h["id"])])
    member_ids = {m["idea_id"] for m in members}
    assert member_ids == {idea_a["id"]}
