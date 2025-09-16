FROM python:3.13-slim

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости приложения
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . .

# Порт, который будет слушать приложение
EXPOSE ${GATEWAY_PORT}