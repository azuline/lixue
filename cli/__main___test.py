from __future__ import annotations

import json

from click.testing import CliRunner

from cli.__main__ import main


def test_idea_crud() -> None:
    runner = CliRunner()

    # Create.
    result = runner.invoke(main, ["idea", "create", "--name", "test idea", "--contents", "some content"])
    assert result.exit_code == 0, result.output
    created = json.loads(result.output)
    assert created["name"] == "test idea"
    assert created["contents"] == "some content"
    assert created["managed"] is False
    assert created["version"] == 1
    idea_id = created["id"]

    # Get by id.
    result = runner.invoke(main, ["idea", "get", str(idea_id)])
    assert result.exit_code == 0, result.output
    fetched = json.loads(result.output)
    assert fetched["id"] == idea_id
    assert fetched["name"] == "test idea"

    # Get by name.
    result = runner.invoke(main, ["idea", "get", "--name", "test idea"])
    assert result.exit_code == 0, result.output
    fetched_by_name = json.loads(result.output)
    assert fetched_by_name["id"] == idea_id

    # List (should contain our idea).
    result = runner.invoke(main, ["idea", "list"])
    assert result.exit_code == 0, result.output
    ideas = [json.loads(line) for line in result.output.strip().splitlines()]
    matching = [i for i in ideas if i["id"] == idea_id]
    assert len(matching) == 1
    assert matching[0]["name"] == "test idea"

    # Update.
    result = runner.invoke(main, ["idea", "update", str(idea_id), "--name", "updated idea"])
    assert result.exit_code == 0, result.output
    updated = json.loads(result.output)
    assert updated["name"] == "updated idea"
    assert updated["contents"] == "some content"
    assert updated["version"] == 2

    # Delete.
    result = runner.invoke(main, ["idea", "delete", str(idea_id)])
    assert result.exit_code == 0, result.output

    # Verify deleted (get should fail).
    result = runner.invoke(main, ["idea", "get", str(idea_id)])
    assert result.exit_code != 0


def test_idea_create_managed() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["idea", "create", "--name", "managed idea", "--managed"])
    assert result.exit_code == 0, result.output
    created = json.loads(result.output)
    assert created["managed"] is True


def test_idea_get_requires_id_or_name() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["idea", "get"])
    assert result.exit_code != 0
