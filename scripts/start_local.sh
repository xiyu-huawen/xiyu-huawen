#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME="$ROOT/../.runtime"
PYTHON="$RUNTIME/python310-expanded/Python_Framework.pkg/Payload/Versions/3.10/bin/python3.10"
export PYTHONPATH="$ROOT/.venv/lib/python3.10/site-packages"
export DYLD_FALLBACK_LIBRARY_PATH="$RUNTIME/homebrew/cairo/1.18.6/lib"
export ADMIN_PASSWORD="${ADMIN_PASSWORD:-preview-only}"
cd "$ROOT"
"$PYTHON" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT
python3 scripts/dev_server.py --port "${PORT:-4191}"
