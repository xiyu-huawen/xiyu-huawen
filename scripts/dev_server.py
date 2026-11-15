#!/usr/bin/env python3
"""Serve the supplied production frontend and proxy its public API locally."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import argparse
import os

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'frontend' / 'dist'), **kwargs)

    def proxy(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length) if length else None
        request = Request(
            'http://127.0.0.1:8000' + self.path,
            data=body,
            method=self.command,
            headers={key: value for key, value in self.headers.items() if key.lower() in {'content-type', 'authorization', 'accept'}},
        )
        try:
            response = urlopen(request, timeout=180)
        except HTTPError as error:
            response = error
        with response:
            payload = response.read()
            self.send_response(response.status)
            for key, value in response.headers.items():
                if key.lower() not in {'connection', 'transfer-encoding', 'content-length'}:
                    self.send_header(key, value)
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            if self.command != 'HEAD':
                self.wfile.write(payload)

    def route(self):
        if self.path.startswith(('/api/', '/assets/', '/import-assets/')):
            self.proxy()
        else:
            super().do_GET()

    do_GET = route
    do_POST = route
    do_PUT = route
    do_DELETE = route

    def log_message(self, fmt, *args):
        if os.getenv('QUIET') != '1':
            super().log_message(fmt, *args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8088)
    args = parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
