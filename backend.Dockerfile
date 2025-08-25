# Backend + Celery image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps (add others as your requirements need)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy backend code
COPY backend /app

# Make sure instance dir exists for config/DB
RUN mkdir -p /app/instance

# Flask dev server port
EXPOSE 8000

# Default command is overridden by docker-compose for each service
CMD ["python", "wsgi.py"]
