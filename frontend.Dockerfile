# Vite dev server
FROM node:20-alpine

WORKDIR /app

# Install deps
COPY frontend/package*.json ./
RUN npm install

# Copy source
COPY frontend/ .

# Vite default dev port
EXPOSE 5173

# Run Vite on 0.0.0.0 so Docker can expose it
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
