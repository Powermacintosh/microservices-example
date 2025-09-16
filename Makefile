up:
	docker compose up

down:
	docker compose down

build:
	docker compose up --build -d

test:
	docker compose -f docker-compose.test.yml up --build -d --remove-orphans
	docker compose -f docker-compose.test.yml exec -it tasks_app_test bash -c "pytest -v"
	docker compose -f docker-compose.test.yml down
