#!make

all: restart logs

up:
	@echo "===== Docker up ====="
	docker compose up

down:
	@echo "===== Docker down ====="
	docker compose down --remove-orphans

start:
	@echo "===== Docker start ====="
	docker compose up -d

stop:
	@echo "===== Docker stop ====="
	docker compose stop

restart:
	@echo "===== Docker restart ====="
	make down
	make start

remove: stop
	@echo "===== Remove containers ====="
	docker compose rm -f

logs:
	@echo "===== Docker logs ====="
	docker compose logs -f

run:
	@echo "===== Docker run container ====="
	docker compose run --rm clickhouse-server bash

exec:
	@echo "===== Docker exec container ====="
	docker compose exec clickhouse-server bash

stats:
	@echo "===== Docker stats ====="
	docker stats

ps:
	@echo "===== Print state of containers ====="
	docker compose ps
