FROM python:3.10-slim

WORKDIR /app

# Встановлюємо системні залежності, необхідні для зйомки/компіляції пакетів (зокрема для asyncpg/psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо Python-залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо решту проєкту
COPY . .

# Команда за замовчуванням для запуску development-сервера з гарячим перезавантаженням
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]