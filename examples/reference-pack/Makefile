.PHONY: doctor demo conformance up down

COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || (command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo ""))

ifneq ($(filter doctor,$(MAKECMDGOALS)),doctor)
ifeq ($(strip $(COMPOSE)),)
$(error Docker Compose command not found. Run `make doctor` for diagnostics)
endif
endif

doctor:
	./scripts/doctor.sh

up:
	$(COMPOSE) -f docker-compose.yml up -d --build gateway

down:
	$(COMPOSE) -f docker-compose.yml down --remove-orphans

demo:
	$(COMPOSE) -f docker-compose.yml up --build runner

conformance:
	$(COMPOSE) -f docker-compose.yml up -d --build gateway
	$(COMPOSE) -f docker-compose.yml run --rm runner bash -lc "bash examples/reference-pack/scripts/conformance.sh"
