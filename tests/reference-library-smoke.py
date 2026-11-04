#!/usr/bin/env python3
"""Offline test of the Pokémon/trainer reference importer; no game artwork required."""
import hashlib
import struct
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai"))
import local_reference_library as library


def chunk(label, content):
    data = label + content
    return struct.pack(">I", len(content)) + data + struct.pack(">I", zlib.crc32(data))


def png(path, width, height):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(b"\0" + (b"\x50\x95\xd0\xff" * width) for _ in range(height))
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    path.write_bytes(data)


with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    source = root / "expansion"
    data = source / "graphics"
    png(data / "pokemon" / "scizor" / "anim_front.png", 64, 128)
    png(data / "pokemon" / "scizor" / "icon.png", 32, 64)
    png(data / "trainers" / "back_pics" / "brendan.png", 64, 256)
    db = root / "private" / "reference.sqlite3"
    first = library.scan(source, db)
    assert first["total"] == 3, first
    assert first["pokemon"] == 2 and first["trainers"] == 1
    assert first["frames"] == 8, first
    assert first["errors"] == 0
    assert library.statistics(db)["training_eligible"] == 0
    assert library.catalog(db, "pokemon", "scizor")["total"] == 2
    assert library.catalog(db, "trainer", "brendan")["total"] == 1
    assert library.catalog(db, "pokemon", "", limit=1)["has_more"] is True
    assert library.catalog(db, "pokemon", "", offset=1, limit=1)["has_more"] is False
    # Repeat import is idempotent and doesn't duplicate entries.
    second = library.scan(source, db)
    assert second["total"] == 3
    assert library.statistics(db)["total"] == 3
    # A changed source file is re-indexed with updated dimensions.
    png(data / "pokemon" / "scizor" / "anim_front.png", 64, 64)
    third = library.scan(source, db)
    assert third["frames"] == 7 and library.statistics(db)["total"] == 3
print("Canvas local sprite reference library test passed.")
