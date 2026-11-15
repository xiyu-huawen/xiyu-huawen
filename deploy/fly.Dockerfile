FROM node:22-slim AS frontend
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

FROM python:3.11-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libcairo2 nginx curl && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.lock /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app/backend
COPY seed /app/seed
COPY --from=frontend /app/dist /usr/share/nginx/html
COPY deploy/fly.nginx.conf /etc/nginx/conf.d/default.conf
COPY deploy/fly-start.sh /app/fly-start.sh
ENV DATA_DIR=/data PYTHONUNBUFFERED=1
RUN mkdir -p /data && chmod +x /app/fly-start.sh
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s CMD curl -f http://127.0.0.1:8080/api/health || exit 1
CMD ["bash", "/app/fly-start.sh"]
