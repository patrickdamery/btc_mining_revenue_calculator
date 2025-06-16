# Variables
BACKEND_DIR=fastapi_backend
FRONTEND_DIR=nextjs-frontend
DOCKER_COMPOSE=docker compose

.PHONY: all clean test

all:
	$(DOCKER_COMPOSE) build db
	$(DOCKER_COMPOSE) up -d db
	$(DOCKER_COMPOSE) run --rm backend alembic upgrade head
	$(DOCKER_COMPOSE) build backend --no-cache
	$(DOCKER_COMPOSE) up -d backend
	$(DOCKER_COMPOSE) up -d celery_beat
	$(DOCKER_COMPOSE) up -d celery_worker
	$(DOCKER_COMPOSE) build frontend --no-cache
	$(DOCKER_COMPOSE) up -d frontend


clean:
	$(DOCKER_COMPOSE) down -v

test:
	$(DOCKER_COMPOSE) run --rm backend pytest
	$(DOCKER_COMPOSE) run --rm frontend pnpm run test
