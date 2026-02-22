.PHONY: demo conformance up down

up:
	docker compose -f docker-compose.yml up -d --build gateway

down:
	docker compose -f docker-compose.yml down --remove-orphans

demo:
	docker compose -f docker-compose.yml up --build runner

conformance:
	docker compose -f docker-compose.yml up -d --build gateway
	docker compose -f docker-compose.yml run --rm runner bash -lc "bash examples/reference-pack/scripts/conformance.sh"
