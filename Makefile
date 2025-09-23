up:
	docker compose --env-file=.env.example up -d

down:
	docker compose --env-file=.env.example down

build:
	docker compose --env-file=.env.example up --build -d

test:
	docker compose -f docker-compose.test.yml --env-file=.env.test up --build -d
	docker compose -f docker-compose.test.yml --env-file=.env.test exec -it tasks_app_test bash -c "pytest -v"
	docker compose -f docker-compose.test.yml --env-file=.env.test down -v --remove-orphans