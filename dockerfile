# Use Python for backend
FROM python:3.10-slim AS backend

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/ .

# Use Node for frontend build
FROM node:18 AS frontend
WORKDIR /frontend
COPY frontend/ .
RUN npm install && npm run dev

# Final stage: serve backend + frontend
FROM python:3.10-slim
WORKDIR /app

# Copy backend + installed packages
COPY --from=backend /app /app
RUN pip install gunicorn

# Copy built Vue frontend into Flask static folder
COPY --from=frontend /frontend/dist /app/dist

# Expose port
EXPOSE 8080

# Start Gunicorn
CMD ["gunicorn", "-b", ":8080", "backend.app:app"]


