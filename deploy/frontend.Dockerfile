ARG NODE_BASE=node:22-slim
ARG NGINX_BASE=nginx:1.26-bookworm
FROM ${NODE_BASE} AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build
FROM ${NGINX_BASE}
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
HEALTHCHECK --interval=15s --timeout=5s CMD service nginx status || exit 1
EXPOSE 80
