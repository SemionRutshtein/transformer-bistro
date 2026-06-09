.PHONY: install run test cov lint format type up down build

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	poetry run pytest -m "not slow" --cov=app --cov-report=term-missing

cov:
	poetry run pytest -m "not slow" --cov=app --cov-report=term-missing --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

slow:
	poetry run pytest -m slow -v

lint:
	poetry run ruff check app tests
	poetry run ruff format --check app tests

format:
	poetry run ruff check --fix app tests
	poetry run ruff format app tests

type:
	poetry run mypy app

up:
	docker compose up --build

down:
	docker compose down

build:
	docker build -f docker/api.Dockerfile -t transformer-bistro-api .
