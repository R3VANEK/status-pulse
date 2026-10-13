setup:
	bash ./scripts/setup

start:
	bash ./scripts/start

make_migrations:
	cd backend && ..\venv\Scripts\python.exe manage.py makemigrations

migrate:
	docker compose exec api python manage.py migrate
