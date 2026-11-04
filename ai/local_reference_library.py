#!/usr/bin/env python3
r"""Canvas AI local sprite reference library.

Scans all Pokémon and trainer PNGs without copying artwork to GitHub.
Usage:
  python ai/local_reference_library.py scan --source "C:\ROM Hacks\Pokemon Brisk Emerald"
  python ai/local_reference_library.py serve --site . --port 8765
"""
from __future__ import annotations

import argparse
import hashlib
import json
from local_generator import capabilities as ai_capabilities, models as ai_models, start_job as ai_start_job, job_status as ai_job_status
import mimetypes
import os
import re
import sqlite3
import struct
import sys
import time
from collections import Counter
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit


def default_db() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    return (Path(root) if root else Path.home() / ".local" / "share") / "CanvasAI" / "references.sqlite3"


def read_png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("Invalid PNG header")
    w, h = struct.unpack(">II", header[16:24])
    if not 1 <= w <= 16384 or not 1 <= h <= 16384:
        raise ValueError("Image dimensions out of bounds")
    return w, h


def frame_shape(width: int, height: int, kind: str) -> tuple[int, int, int]:
    """Infer actual sprite cells when a sheet is a regular 16/32/64/80 grid."""
    # For narrow tilesheets such as 8x800, do not invent hundreds of frames.
    if width < 16 or height < 16:
        return width, height, 1
    if width == 64 and height % 64 == 0:
        side = 64
    elif height == 64 and width % 64 == 0:
        side = 64
    elif width % 32 == 0 and height % 32 == 0 and (width == 32 or height == 32):
        side = 32
    elif width == 80 and height % 80 == 0:
        side = 80
    elif width == 16 and height % 16 == 0:
        side = 16
    else:
        return width, height, 1
    return side, side, (width // side) * (height // side)


def create_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sprites (
      id TEXT PRIMARY KEY,
      category TEXT NOT NULL CHECK(category IN ('pokemon','trainer')),
      label TEXT NOT NULL, kind TEXT NOT NULL,
      relpath TEXT UNIQUE NOT NULL,
      width INTEGER NOT NULL, height INTEGER NOT NULL,
      frame_width INTEGER NOT NULL, frame_height INTEGER NOT NULL,
      frame_count INTEGER NOT NULL,
      sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
      permission_state TEXT NOT NULL DEFAULT 'unreviewed',
      train_allowed INTEGER NOT NULL DEFAULT 0,
      scan_id TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS sprites_category_label ON sprites(category, label);
    CREATE INDEX IF NOT EXISTS sprites_kind ON sprites(kind);
    CREATE INDEX IF NOT EXISTS sprites_sha ON sprites(sha256);
    """)


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(131072), b""):
            digest.update(block)
    return digest.hexdigest()


def scan(source: Path, database: Path) -> dict:
    source = source.expanduser().resolve()
    graphics = source / "graphics"
    if not (graphics / "pokemon").is_dir() or not (graphics / "trainers").is_dir():
        raise FileNotFoundError(f"Expected graphics/pokemon and graphics/trainers under {source}")
    database.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(database)
    create_db(conn)
    scan_id = str(time.time_ns())
    counts: Counter[str] = Counter()
    failures: list[dict] = []
    with conn:
        for category, dirname in (("pokemon", "pokemon"), ("trainer", "trainers")):
            folder = graphics / dirname
            for path in sorted(folder.rglob("*")):
                if not path.is_file() or path.suffix.lower() != ".png":
                    continue
                rel = path.relative_to(graphics).as_posix()
                try:
                    w, h = read_png_dimensions(path)
                    kind = path.stem.lower()
                    frame_w, frame_h, nframes = frame_shape(w, h, kind)
                    # Pokémon label: species/form folder; trainer: parent/subfolder plus stem.
                    parts = path.relative_to(folder).parts
                    label = (" / ".join(parts[:-1]) if category == "pokemon" else " / ".join(parts[:-1] + (path.stem,)))
                    if not label:
                        label = path.stem
                    ident = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:24]
                    size = path.stat().st_size
                    sha = digest_file(path)
                    conn.execute("""
                    INSERT INTO sprites
                    (id,category,label,kind,relpath,width,height,frame_width,frame_height,frame_count,
                     sha256,bytes,permission_state,train_allowed,scan_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(id) DO UPDATE SET
                      category=excluded.category,label=excluded.label,kind=excluded.kind,
                      relpath=excluded.relpath,width=excluded.width,height=excluded.height,
                      frame_width=excluded.frame_width,frame_height=excluded.frame_height,
                      frame_count=excluded.frame_count,bytes=excluded.bytes,
                      permission_state=CASE WHEN sprites.sha256=excluded.sha256
                        THEN sprites.permission_state ELSE 'unreviewed' END,
                      train_allowed=CASE WHEN sprites.sha256=excluded.sha256
                        THEN sprites.train_allowed ELSE 0 END,
                      sha256=excluded.sha256,scan_id=excluded.scan_id
                    """, (ident, category, label, kind, rel, w, h, frame_w, frame_h, nframes,
                          sha, size, "unreviewed", 0, scan_id))
                    counts[category] += 1
                    counts["frames"] += nframes
                except (OSError, ValueError) as e:
                    failures.append({"file": rel, "reason": str(e)})
        conn.execute("DELETE FROM sprites WHERE scan_id != ?", (scan_id,))
        conn.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('source_root', ?)", (str(graphics),))
        conn.execute("INSERT OR REPLACE INTO metadata(key,value) VALUES('last_scan', ?)", (scan_id,))
    result = {
        "pokemon": counts["pokemon"], "trainers": counts["trainer"],
        "total": counts["pokemon"] + counts["trainer"], "frames": counts["frames"],
        "errors": len(failures), "error_examples": failures[:20],
        "database": str(database), "source": str(graphics),
        "training_eligible": 0, "copyright_notice": "Cataloged locally; no right to train or redistribute is implied."
    }
    conn.close()
    return result


def connection(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    return db


def catalog(db: Path, category: str = "all", query: str = "", offset: int = 0, limit: int = 60) -> dict:
    offset = max(0, min(offset, 1_000_000))
    limit = max(1, min(limit, 100))
    where: list[str] = []
    args: list[str] = []
    if category in ("pokemon", "trainer"):
        where.append("category=?")
        args.append(category)
    if query:
        q = query[:100].replace("%", r"\%").replace("_", r"\_")
        where.append("(label LIKE ? ESCAPE '\\' OR kind LIKE ? ESCAPE '\\' OR relpath LIKE ? ESCAPE '\\')")
        args.extend(["%" + q + "%"] * 3)
    clause = " WHERE " + " AND ".join(where) if where else ""
    with closing(connection(db)) as conn:
        total = conn.execute("SELECT COUNT(*) FROM sprites" + clause, args).fetchone()[0]
        rows = conn.execute("SELECT id,category,label,kind,width,height,frame_width,frame_height,frame_count,bytes,permission_state,train_allowed FROM sprites"
                            + clause + " ORDER BY category,label,kind LIMIT ? OFFSET ?", [*args, limit, offset]).fetchall()
    return {"items": [dict(row) for row in rows], "total": total, "offset": offset,
            "limit": limit, "has_more": offset + len(rows) < total}


def statistics(db: Path) -> dict:
    with closing(connection(db)) as conn:
        counts = {row[0]: row[1] for row in conn.execute("SELECT category,COUNT(*) FROM sprites GROUP BY category")}
        frames = conn.execute("SELECT COALESCE(SUM(frame_count),0) FROM sprites").fetchone()[0]
        eligible = conn.execute("SELECT COUNT(*) FROM sprites WHERE train_allowed=1").fetchone()[0]
    return {"pokemon": counts.get("pokemon", 0), "trainers": counts.get("trainer", 0),
            "total": sum(counts.values()), "frames": frames,
            "training_eligible": eligible, "mode": "local_reference_only",
            "notice": "Indexed source art is not automatically authorized for AI training or redistribution."}


def serve(db_path: Path, site: Path, host: str, port: int) -> None:
    site = site.resolve()
    if host not in ("127.0.0.1", "localhost"):
        raise ValueError("Local reference server must bind to localhost")
    if not (site / "index.html").is_file():
        raise FileNotFoundError(f"Missing Canvas index.html in {site}")
    if not db_path.is_file():
        raise FileNotFoundError(f"Missing reference index: {db_path}; run scan first")
    with closing(connection(db_path)) as conn:
        metadata = conn.execute("SELECT value FROM metadata WHERE key='source_root'").fetchone()
    if not metadata:
        raise ValueError("Database does not have a source root")
    graphics = Path(metadata[0]).resolve()
    allowed = (graphics / "pokemon", graphics / "trainers")
    if not all(p.is_dir() for p in allowed):
        raise FileNotFoundError(f"Sprite folders moved: {graphics}; rerun scan")

    class Handler(BaseHTTPRequestHandler):
        def send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "private, no-store")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def send_json(self, obj: object, status: int = 200) -> None:
            self.send_bytes(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                            "application/json; charset=utf-8", status)

        def valid_origin(self) -> bool:
            host_header = self.headers.get("Host", "").split(":")[0].lower()
            origin = self.headers.get("Origin")
            fetch_site = self.headers.get("Sec-Fetch-Site","")
            # No cross-site POSTs, and no localhost browser requests to this process from other sites.
            return (host_header in ("localhost","127.0.0.1")
                    and (not origin or origin in (f"http://localhost:{port}", f"http://127.0.0.1:{port}"))
                    and fetch_site not in ("cross-site", "same-site"))

        def do_POST(self) -> None:
            if not self.valid_origin():
                return self.send_json({"error":"Local origin required"},403)
            if self.path != "/api/v1/generations":
                return self.send_json({"error":"Not found"},404)
            try:
                size = int(self.headers.get("Content-Length","0"))
            except ValueError:
                return self.send_json({"error":"Invalid Content-Length"},400)
            if size < 2 or size > 15_000_000:
                return self.send_json({"error":"Request must be 2 bytes to 15MB"},413)
            try:
                params = json.loads(self.rfile.read(size))
                data = ai_start_job(params, graphics, db_path)
            except (ValueError,TypeError,json.JSONDecodeError) as error:
                return self.send_json({"error":str(error)[:240]},400)
            return self.send_json(data,202)

        def do_GET(self) -> None:
            if not self.valid_origin():
                return self.send_json({"error": "Local origin required"}, 403)
            parsed = urlsplit(self.path)
            path = unquote(parsed.path)
            params = parse_qs(parsed.query)
            if path in ("/", "/index.html"):
                return self.send_bytes((site / "index.html").read_bytes(), "text/html; charset=utf-8")
            if path == "/api/v1/references":
                try:
                    off = int(params.get("offset", ["0"])[0])
                    limit = int(params.get("limit", ["60"])[0])
                except ValueError:
                    return self.send_json({"error": "offset/limit must be integers"}, 400)
                return self.send_json(catalog(db_path, params.get("category", ["all"])[0],
                                              params.get("q", [""])[0], off, limit))
            if path in ("/api/v1/stats", "/api/v1/health"):
                result = statistics(db_path)
                if path.endswith("/health"):
                    result["ai"] = ai_capabilities()
                return self.send_json(result)
            if path == "/api/v1/models":
                return self.send_json({"models":ai_models(),"device":ai_capabilities()})
            gen_match = re.fullmatch(r"/api/v1/generations/([a-f0-9]{32})",path)
            if gen_match:
                job=ai_job_status(gen_match.group(1))
                return self.send_json(job) if job else self.send_json({"error":"Job not found"},404)
            match = re.fullmatch(r"/api/v1/references/([a-f0-9]{24})/image", path)
            if match:
                with closing(connection(db_path)) as conn:
                    row = conn.execute("SELECT relpath FROM sprites WHERE id=?", (match.group(1),)).fetchone()
                if not row:
                    return self.send_json({"error": "Image not found"}, 404)
                candidate = (graphics / row[0]).resolve()
                if not any(candidate.is_relative_to(p) for p in allowed) or candidate.suffix.lower() != ".png":
                    return self.send_json({"error": "Access denied"}, 403)
                try:
                    return self.send_bytes(candidate.read_bytes(), "image/png")
                except OSError:
                    return self.send_json({"error": "Image source moved; rerun scan"}, 404)
            return self.send_json({"error": "Not found"}, 404)

        def log_message(self, fmt: str, *args: object) -> None:
            if not self.path.startswith("/api/v1/references/"):
                super().log_message(fmt, *args)

    print(f"Canvas reference library: http://{host}:{port}", flush=True)
    print(f"Using {db_path} | source {graphics}", flush=True)
    with ThreadingHTTPServer((host, port), Handler) as server:
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    scanner = sub.add_parser("scan", help="Index all trainer and Pokémon PNGs without copying artwork")
    scanner.add_argument("--source", required=True, type=Path)
    scanner.add_argument("--db", type=Path, default=default_db())
    srv = sub.add_parser("serve", help="Serve Canvas and searchable local reference library")
    srv.add_argument("--db", type=Path, default=default_db())
    srv.add_argument("--site", type=Path, default=Path(__file__).resolve().parent.parent)
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "scan":
        print(json.dumps(scan(args.source, args.db), indent=2))
    else:
        serve(args.db, args.site, args.host, args.port)


if __name__ == "__main__":
    main()
