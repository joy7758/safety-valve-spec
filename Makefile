.PHONY: conformance registry-check registry-export venv

venv:
	python3 -m venv .venv
	. .venv/bin/activate && python3 -m pip install -U pip && python3 -m pip install cryptography fastapi uvicorn

conformance:
	. .venv/bin/activate && bash conformance/run.sh

registry-export:
	python3 tools/registry_export.py

registry-check:
	@before="$$(git status --porcelain)"; \
	python3 tools/registry_export.py; \
	python3 tools/registry_export.py; \
	test -f registry/svs-types-v0.2.json; \
	test -f registry/svs-reason-codes-v0.2.json; \
	test -f registry/svs-profiles-v0.2.json; \
	after="$$(git status --porcelain)"; \
	test "$$before" = "$$after"
