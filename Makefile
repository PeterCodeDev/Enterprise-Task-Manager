.PHONY: build up down test migrate seed lint

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

test:
	docker-compose run --rm backend pytest tests/ -v

migrate:
	docker-compose run --rm backend alembic upgrade head

migration name:
	docker-compose run --rm backend alembic revision --autogenerate -m "$(name)"

lint:
	cd backend && ruff check . --fix && ruff format .

seed:
	docker-compose exec backend python -c "from app.seed import run; run()"

logs:
	docker-compose logs -f backend

shell:
	docker-compose exec backend python

clean:
	docker-compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache__ backend/tests/__pycache__
	rm -rf frontend/node_modules frontend/dist
