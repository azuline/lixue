check: typecheck test lintcheck

typecheck:
	ty check

test:
	pytest -n logical .
	coverage html

snapshot:
	pytest --snapshot-update .

lintcheck:
	ruff format --check .
	ruff check .

lint:
	ruff format .
	ruff check --fix .

clean:
	git clean -xdf

.PHONY: check test typecheck lintcheck lint clean snapshot
