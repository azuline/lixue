from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import click


@click.command()
def main() -> None:
    root = Path(__file__).resolve().parent.parent.parent

    # Clean up existing __codegen__ directories.
    for codegen_dir in root.rglob("__codegen__"):
        if codegen_dir.is_dir():
            shutil.rmtree(codegen_dir)

    # Dump the current schema from the yoyo migrations.
    schema_sql = root / "schema.sql"
    _dump_schema(root, schema_sql)

    # Run sqlc generate.
    click.echo("Running sqlc generate...")
    subprocess.run(["sqlc", "generate", "-f", str(root / "sqlc.yaml")], check=True, cwd=root)
    click.echo("Codegen completed successfully.")


def _dump_schema(root: Path, schema_sql: Path) -> None:
    import sqlite3
    import tempfile

    from yoyo import get_backend, read_migrations

    migrations_dir = root / "migrations"

    with tempfile.NamedTemporaryFile(suffix=".db", delete=True) as tmp:
        tmp_path = tmp.name

    try:
        backend = get_backend(f"sqlite:///{tmp_path}")
        migrations = read_migrations(str(migrations_dir))
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

        conn = sqlite3.connect(tmp_path)
        try:
            cursor = conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE '_yoyo%' AND name NOT LIKE 'yoyo%' ORDER BY CASE type WHEN 'table' THEN 0 WHEN 'index' THEN 1 WHEN 'view' THEN 2 ELSE 3 END, name")
            statements = [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()

        with schema_sql.open("w") as f:
            f.write("-- Auto-generated from migrations. Do not hand-edit.\n")
            f.write("-- Regenerate with: python -m tools.codegen_db\n\n")
            for stmt in statements:
                f.write(stmt + ";\n\n")

        click.echo(f"Schema dumped to {schema_sql}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
