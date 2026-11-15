#!/usr/bin/env python3
"""Chunked local multi-agent workspace inbox; standard library only."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, quote, urlparse
import json
import os
import re
import threading
import uuid

HERE = Path(__file__).resolve().parent
INBOX = HERE / "inbox"
TEMP = HERE / ".uploads"
CHUNK_LIMIT = 16 * 1024 * 1024
_LOCK = threading.Lock()


def safe_relative(raw: str) -> Path:
    raw = raw.replace("\\", "/")
    path = PurePosixPath(raw)
    if not raw or path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError("Invalid relative path")
    if path.parts and re.fullmatch(r"[A-Za-z]:", path.parts[0]):
        raise ValueError("Absolute paths are not accepted")
    return Path(*path.parts)


class Handler(BaseHTTPRequestHandler):
    server_version = "SharedWorkspace/1.0"

    def _json(self, status: int, body: dict) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/status":
            INBOX.mkdir(parents=True, exist_ok=True)
            self._json(200, {"status": "ready", "chunk_bytes": CHUNK_LIMIT,
                             "inbox": "coordination/shared-workspace/inbox"})
            return
        if route == "/api/files":
            INBOX.mkdir(parents=True, exist_ok=True)
            items = []
            for candidate in INBOX.rglob("*"):
                if candidate.is_symlink() or not candidate.is_file():
                    continue
                try:
                    stat = candidate.stat()
                    items.append({"path": candidate.relative_to(INBOX).as_posix(),
                                  "bytes": stat.st_size, "modified": int(stat.st_mtime)})
                except OSError:
                    continue
            items.sort(key=lambda item: item["path"].casefold())
            self._json(200, {"files": items, "count": len(items),
                             "total_bytes": sum(item["bytes"] for item in items)})
            return
        if route == "/api/download":
            params = parse_qs(urlparse(self.path).query)
            try:
                relative = safe_relative(params["path"][0])
                candidate = INBOX / relative
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(INBOX.resolve())
                if candidate.is_symlink() or not resolved.is_file():
                    raise ValueError("Not a regular inbox file")
                size = resolved.stat().st_size
            except (KeyError, IndexError, OSError, ValueError):
                self._json(404, {"error": "File not found"})
                return
            filename = quote(resolved.name, safe="")
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f"attachment; filename=download; filename*=UTF-8''{filename}")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "private, no-store")
            self.end_headers()
            try:
                with resolved.open("rb") as source:
                    while block := source.read(1024 * 1024):
                        self.wfile.write(block)
            except (BrokenPipeError, ConnectionResetError):
                pass
            return
        if route in ("/", "/index.html"):
            page = HERE / "index.html"
            data = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/upload":
            self._json(404, {"error": "Not found"})
            return
        params = parse_qs(urlparse(self.path).query)
        try:
            upload_id = params["id"][0]
            if not re.fullmatch(r"[0-9a-f-]{36}", upload_id):
                raise ValueError("Invalid upload id")
            relative = safe_relative(params["path"][0])
            offset = int(params["offset"][0])
            total = int(params["total"][0])
            done = params.get("done", ["0"])[0] == "1"
            length = int(self.headers.get("Content-Length", "-1"))
            if offset < 0 or total < 0 or length < 0 or length > CHUNK_LIMIT or offset + length > total:
                raise ValueError("Invalid chunk size or offset")
        except (KeyError, IndexError, ValueError) as exc:
            self._json(400, {"error": str(exc) or "Invalid upload request"})
            return

        TEMP.mkdir(parents=True, exist_ok=True)
        temp_file = TEMP / (upload_id + ".part")
        try:
            with _LOCK:
                current = temp_file.stat().st_size if temp_file.exists() else 0
                if current != offset:
                    self._json(409, {"error": "Chunk offset mismatch", "expected_offset": current})
                    return
                with temp_file.open("ab") as target:
                    remaining = length
                    while remaining:
                        data = self.rfile.read(min(1024 * 1024, remaining))
                        if not data:
                            raise ConnectionError("Client ended upload before chunk completed")
                        target.write(data)
                        remaining -= len(data)
                current += length
                if done:
                    if current != total:
                        self._json(400, {"error": "Upload ended before declared file size", "received": current})
                        return
                    destination = INBOX / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    # Never overwrite an existing handoff; generate a stable unique name.
                    with_destination = destination
                    if with_destination.exists():
                        stem, suffix = destination.stem, destination.suffix
                        number = 2
                        while with_destination.exists():
                            with_destination = destination.with_name(f"{stem} ({number}){suffix}")
                            number += 1
                    os.replace(temp_file, with_destination)
                    self._json(201, {"status": "saved", "path": with_destination.relative_to(INBOX).as_posix(),
                                     "bytes": current})
                else:
                    self._json(200, {"status": "chunk_saved", "received": current, "total": total})
        except (OSError, ConnectionError) as exc:
            self._json(500, {"error": f"Upload failed: {exc}"})

    def log_message(self, fmt: str, *args) -> None:
        print("[workspace] " + fmt % args)


def main() -> None:
    INBOX.mkdir(parents=True, exist_ok=True)
    TEMP.mkdir(parents=True, exist_ok=True)
    host = os.environ.get("WORKSPACE_HOST", "0.0.0.0")
    port = int(os.environ.get("WORKSPACE_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Shared workspace ready at http://{host}:{port}")
    print(f"Files are saved under {INBOX}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
