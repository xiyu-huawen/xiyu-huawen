import os
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DATA_DIR', str(ROOT / 'runtime'))

from a2wsgi import ASGIMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app import app

class LazyASGI:
    def __init__(self, asgi_app):
        self.asgi_app = asgi_app
        self.middleware = None
        self.lock = threading.Lock()

    def __call__(self, environ, start_response):
        if self.middleware is None:
            with self.lock:
                if self.middleware is None:
                    self.middleware = ASGIMiddleware(self.asgi_app)
        return self.middleware(environ, start_response)


api = LazyASGI(app)
frontend = LazyASGI(StaticFiles(directory=ROOT / 'frontend' / 'dist', html=True))


def application(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path.startswith(('/api/', '/assets/', '/import-assets/')):
        return api(environ, start_response)
    return frontend(environ, start_response)
