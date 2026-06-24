.PHONY: up down logs reset seed test evaluate

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api worker edge-service

reset:
	docker compose down -v
	docker compose up -d postgres redis

seed:
	python scripts/seed/reset.py

test:
	python -m pytest tests/platform

evaluate:
	python scripts/evaluate/list.py

