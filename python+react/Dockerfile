# Frontend build stage
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend build stage
FROM python:3.11-slim AS backend-build
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app

# Install Node.js and ffmpeg for serving frontend and backend
RUN apt-get update && \
    apt-get install -y nodejs npm ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-build /app/backend/venv /app/backend/venv
COPY backend/ /app/backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PATH="/app/backend/venv/bin:$PATH"
ENV API_URL=http://localhost:5000

# Copy startup script
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 5000 3000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
