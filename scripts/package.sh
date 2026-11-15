#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p outputs/1.3.0
for arch in arm64 amd64; do
  for service in api web; do
    case "$service" in api) dockerfile=deploy/backend.Dockerfile;; web) dockerfile=deploy/frontend.Dockerfile;; esac
    if [ "$arch" = amd64 ] && [ "$service" = api ]; then
      docker buildx build --platform "linux/$arch" --load --build-arg PYTHON_BASE=registry-1.docker.io/library/python:3.11-slim-bookworm -f "$dockerfile" -t "xiyuhuawen-$service:1.3.0-$arch" .
    elif [ "$arch" = amd64 ]; then
      docker buildx build --platform "linux/$arch" --load --build-arg NODE_BASE=registry-1.docker.io/library/node:22-slim --build-arg NGINX_BASE=registry-1.docker.io/library/nginx:1.26-bookworm -f "$dockerfile" -t "xiyuhuawen-$service:1.3.0-$arch" .
    else
      docker buildx build --platform "linux/$arch" --load -f "$dockerfile" -t "xiyuhuawen-$service:1.3.0-$arch" .
    fi
  done
  docker save "xiyuhuawen-api:1.3.0-$arch" "xiyuhuawen-web:1.3.0-$arch" | gzip > "outputs/1.3.0/xiyuhuawen-1.3.0-$arch.tar.gz"
done
shasum -a 256 outputs/1.3.0/xiyuhuawen-1.3.0-*.tar.gz > outputs/1.3.0/SHA256SUMS
