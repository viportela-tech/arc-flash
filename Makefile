COMPOSE=docker compose
DB_URL=postgresql://arcflash:arcflash_dev_password@localhost:5432/arcflash

.PHONY: dev test logs db-migrate db-reset docker-clean ps

dev:
	$(COMPOSE) up --build

test:
	$(COMPOSE) config

logs:
	$(COMPOSE) logs -f --tail=200

ps:
	$(COMPOSE) ps

db-migrate:
	$(COMPOSE) up -d db
	$(COMPOSE) exec -T db sh -c 'for file in /migrations/*.sql; do psql -U arcflash -d arcflash -v ON_ERROR_STOP=1 -f "$$file"; done'

db-reset:
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	$(COMPOSE) exec -T db sh -c 'for file in /migrations/*.sql; do psql -U arcflash -d arcflash -v ON_ERROR_STOP=1 -f "$$file"; done'

docker-clean:
	$(COMPOSE) down --remove-orphans
	docker system df
