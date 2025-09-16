#!/bin/bash
set -e

# Ожидаем пока база данных будет готова
echo "Ожидание пока база данных будет готова..."
until PGPASSWORD="${TASKS_DB_PASS}" psql -h "${TASKS_DB_HOST}" -U "${TASKS_DB_USER}" -c '\q'; do
  echo "PostgreSQL недоступен - ожидание..."
  sleep 1
done

# Удаляем базу, если она существует
echo "Удаление существующей базы..."
PGPASSWORD="${TASKS_DB_PASS}" psql -h "${TASKS_DB_HOST}" -U "${TASKS_DB_USER}" -c "DROP DATABASE IF EXISTS \"${TASKS_DB_NAME}\";"

# Создаем новую базу
echo "Создание новой базы..."
PGPASSWORD="${TASKS_DB_PASS}" psql -h "${TASKS_DB_HOST}" -U "${TASKS_DB_USER}" -c "CREATE DATABASE \"${TASKS_DB_NAME}\" WITH ENCODING 'UTF8';"

# Выполняем миграции
echo "Выполнение миграций..."
cd /app
export PYTHONPATH=/app

# Удаляем старые миграции и создаем новые
rm -rf /app/migrations/versions/*
poetry run alembic revision --autogenerate -m 'Initial'
poetry run alembic upgrade head

echo "Инициализация базы данных завершена!"
exec "$@"