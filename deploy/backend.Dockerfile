ARG PYTHON_BASE=python:3.11-slim-bookworm
FROM ${PYTHON_BASE}
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libcairo2 && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.lock /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend /app/backend
COPY seed /app/seed
ENV DATA_DIR=/data PYTHONUNBUFFERED=1
RUN mkdir /data && chown -R 10001:10001 /data /app
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
