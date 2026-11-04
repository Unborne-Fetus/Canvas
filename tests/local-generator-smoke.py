#!/usr/bin/env python3
"""Fast reference-guided inference data-path smoke test, no torch or model download."""
import base64
import io
import sqlite3
import sys
import tempfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai"))
import local_generator as g

with tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    graphics = directory / "graphics"
    source = graphics / "pokemon" / "scizor" / "anim_front.png"
    source.parent.mkdir(parents=True)
    canvas = Image.new("RGBA", (64, 128), (0, 0, 0, 0))
    canvas.paste((190, 30, 40, 255), (10, 8, 52, 53))
    canvas.paste((5, 80, 190, 255), (20, 74, 42, 100))
    canvas.save(source)
    db = directory / "refs.sqlite3"
    with sqlite3.connect(db) as conn:
        conn.execute("CREATE TABLE sprites(id TEXT, relpath TEXT, frame_width INTEGER, frame_height INTEGER, frame_count INTEGER, width INTEGER,height INTEGER)")
        conn.execute("INSERT INTO sprites VALUES(?,?,?,?,?,?,?)",
                     ("a"*24, "pokemon/scizor/anim_front.png", 64, 64, 2, 64, 128))
    img = g.select_frame(graphics, db, {"id": "a"*24, "frame": 1})
    assert img.getpixel((25, 15))[:3] == (5, 80, 190)
    assert img.size == (64, 64)
    assert g.select_frame(graphics, db, {"id": "a"*24, "frame": 0}).getpixel((25, 15))[:3] == (190, 30, 40)
    try:
        g.select_frame(graphics, db, {"id": "a"*24, "frame": 2})
        assert False, "Bad frame should fail"
    except ValueError:
        pass
    raw = g.png_data(img)
    assert g.decode_png_data(raw).size == (64, 64)
    assert g.references_montage([img, img]).size == (512, 512)
    result = g.spriteize(g.references_montage([img]), 24)
    assert result.size == (64, 64) and result.mode == "RGBA"
    assert len(g.models()) == 2
    assert g.capabilities()["installed"] in (True, False)
print("Canvas local generator preprocessing smoke test passed")
