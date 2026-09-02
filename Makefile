.PHONY: install dev test lint fmt run docker clean

VENV := .venv
PY := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: $(VENV)/bin/activate
	$(PIP) install -e ".[dev]"

test: install
	$(VENV)/bin/pytest -v

lint: install
	$(VENV)/bin/ruff check src tests
	$(VENV)/bin/mypy src

fmt: install
	$(VENV)/bin/ruff format src tests

run: install
	$(VENV)/bin/uvicorn mailvert.api.app:app --reload

docker:
	docker compose up --build

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache **/__pycache__
