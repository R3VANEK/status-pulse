.DEFAULT_GOAL := help
.PHONY: help setup start make_migrations migrate shell compile_requirements

help: ## Show all available commands
	@echo =================
	@echo Available Commands
	@echo =================
	@$(MAKE) --no-print-directory _help

_help:
	@echo   help                   - Show all available commands
	@echo   setup                  - Run the project setup script
	@echo   start                  - Restart Docker Compose services
	@echo   make_migrations        - Generate Django database migrations
	@echo   migrate                - Apply Django database migrations
	@echo   shell                  - Open the Django shell inside the API container
	@echo   compile_requirements   - Compile backend requirements files

setup: ## Run the project setup script
	bash ./scripts/setup

start: ## Restart and start Docker Compose services
	docker compose down --remove-orphans
	docker compose up

make_migrations: ## Generate Django database migrations
	cd backend && ..\venv\Scripts\python.exe manage.py makemigrations

migrate: ## Apply Django database migrations
	docker compose exec api python manage.py migrate

shell: ## Open the Django shell inside the API container
	docker compose exec api python manage.py shell

compile_requirements: ## Compile production and development requirements
	pip-compile ./build/backend/requirements.in -o ./build/backend/requirements.txt
	pip-compile ./build/backend/requirements-dev.in -o ./build/backend/requirements-dev.txt

populate: ## Flush old data and populate fresh test data
	docker compose exec api python manage.py flush --noinput
	docker compose exec api python -m statusPulse.populate

REFRESH_DB ?= true

test: ## invoke tests e.g make test -k "test_my_awesome_example"
	docker compose -p status-pulse-test -f docker-compose.test.yaml up -d
	docker compose -p status-pulse-test -f docker-compose.test.yaml exec api pytest --refresh-db=$(REFRESH_DB) $(ARGS)
	docker compose -p status-pulse-test -f docker-compose.test.yaml down
