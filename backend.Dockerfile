FROM python:3.11-slim

WORKDIR /app
COPY backend/ /app

RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Expose Flask API on port 5000
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
