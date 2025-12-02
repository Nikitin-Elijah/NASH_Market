FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry
RUN pip install poetry


COPY pyproject.toml poetry.lock* ./


# Настройка poetry
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --no-root

COPY . .

# Запуск бота
CMD ["python", "-m", "src.main"]