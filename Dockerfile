# =========================================
# Stage 1: Builder
# =========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Install build tools required for Python dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list.
COPY requirements.txt .

# Install Python dependencies into a separate directory.
RUN python -m pip install \
    --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


# =========================================
# Stage 2: Runtime
# =========================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only installed dependencies from builder.
COPY --from=builder /install /usr/local

# Copy application source code.
COPY app ./app

EXPOSE 8000

# Start FastAPI application.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]