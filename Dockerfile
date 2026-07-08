# syntax=docker/dockerfile:1

# Stage 1: Build the Next.js Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
# We run build to generate the static files (.next)
RUN npm run build

# Stage 2: Build the FastAPI Backend
FROM python:3.11-slim AS backend
WORKDIR /app/backend
COPY backend/requirements.txt .
# Install PyTorch with CPU/ROCm compatibility and other ML deps
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Runner Image
FROM python:3.11-slim
WORKDIR /app

# Copy the built backend
COPY --from=backend /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY backend/ ./backend/

# Copy the built frontend (assuming we want to serve it, though Next.js usually runs its own node server)
# For a pure dockerized deployment, we can expose both ports or have FastAPI serve static files.
COPY --from=frontend-builder /app/frontend /app/frontend

# Install Node.js in the final container to run the Next.js production server alongside FastAPI
RUN apt-get update && apt-get install -y nodejs npm supervisor && rm -rf /var/lib/apt/lists/*

# Setup Supervisor to run both the Python backend and Node frontend
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 3000 8000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
