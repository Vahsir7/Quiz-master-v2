# Stage 1: Build Vue frontend
FROM node:20 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/ ./backend/

# Copy built frontend into Flask static folder
COPY --from=frontend-build /app/frontend/dist ./backend/app/static

# Expose the port the app runs on
EXPOSE 8080

# The command to run the application will be handled by Docker Compose