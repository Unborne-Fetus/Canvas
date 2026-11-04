#!/usr/bin/env python3
"""Per-device blank install + optional local source + origin isolation tests.

Exercises actual HTTP service without downloading any model or copying game assets.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def read(url: str) -> dict:
    with urlopen(url, timeout=5) as handle:
        return json.load(handle)


def post(url: str, obj: dict, headers: dict | None = None):
    request = Request(
        url,
        data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json", **(headers or {})},
        method="POST",
    )
    with urlopen(request, timeout=15) as handle:
        return json.load(handle)


with tempfile.TemporaryDirectory() as tmp:
    temp = Path(tmp)
    db = temp / "canvas" / "references.sqlite3"
    source = temp / "personal-expansion"
    sprite = source / "graphics" / "pokemon" / "testbug" / "anim_front.png"
    trainer = source / "graphics" / "trainers" / "front_pics" / "test_trainer.png"
    sprite.parent.mkdir(parents=True)
    trainer.parent.mkdir(parents=True)
    Image.new("RGB", (64, 128), (180, 30, 60)).save(sprite)
    Image.new("RGB", (64, 64), (30, 150, 90)).save(trainer)

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "ai" / "local_reference_library.py"),
         "serve", "--db", str(db), "--site", str(ROOT), "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(100):
            try:
                start = read(base + "/api/v1/stats")
                break
            except (ConnectionError, URLError, TimeoutError):
                if process.poll() is not None:
                    raise AssertionError(f"Service exited unexpectedly: {process.returncode}")
                time.sleep(0.1)
        else:
            raise AssertionError("Service did not start without any references")
        assert start["total"] == 0 and start["source_connected"] is False, start
        assert read(base + "/api/v1/references")["items"] == []

        with urlopen(base + "/", timeout=5) as resp:
            html = resp.read().decode("utf-8")
        assert 'id="aiStudioDialog"' in html
        assert 'id="refsScan"' in html
        assert 'id="aiAllowCpu"' in html

        try:
            post(base + "/api/v1/references/scan", {"source": str(source)},
                 {"Origin": "https://unauthorized.example"})
            raise AssertionError("A cross-origin scan should be denied")
        except HTTPError as denied:
            assert denied.code == 403

        imported = post(base + "/api/v1/references/scan", {"source": str(source)})
        assert imported["total"] == 2, imported
        assert imported["trainers"] == 1 and imported["pokemon"] == 1
        updated = read(base + "/api/v1/stats")
        assert updated["total"] == 2 and updated["source_connected"] is True, updated
        items = read(base + "/api/v1/references?category=pokemon&q=testbug")
        assert items["total"] == 1 and len(items["items"]) == 1
        image_url = base + "/api/v1/references/" + items["items"][0]["id"] + "/image"
        with urlopen(image_url, timeout=5) as handle:
            assert handle.read(8) == b"\x89PNG\r\n\x1a\n"

        print("Portable Canvas AI service: empty device, local import, trainer/Pokémon index, HTTP origin isolation — PASSED")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
