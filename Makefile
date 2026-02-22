.PHONY: conformance venv

venv:
	python3 -m venv .venv
	. .venv/bin/activate && python -m pip install -U pip && python -m pip install cryptography fastapi uvicorn

conformance:
	. .venv/bin/activate && bash conformance/run.sh
