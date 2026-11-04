#!/usr/bin/env python3
"""Fast reference-guided inference data-path smoke test, no torch or model download."""
import base64
from contextlib import closing
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
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("CREATE TABLE sprites(id TEXT, relpath TEXT, frame_width INTEGER, frame_height INTEGER, frame_count INTEGER, width INTEGER,height INTEGER)")
        conn.execute("INSERT INTO sprites VALUES(?,?,?,?,?,?,?)",
                     ("a"*24, "pokemon/scizor/anim_front.png", 64, 64, 2, 64, 128))
        conn.commit()
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
    # The main reference should fill a substantial part of the 512px guide.
    guide = g.subject_crop(img)
    foreground = sum(1 for rgb in guide.get_flattened_data() if rgb != (236, 238, 242))
    assert foreground > 40000, foreground
    result = g.spriteize(g.references_montage([img]), 24)
    assert result.size == (64, 64) and result.mode == "RGBA"
    mask = g.reference_alpha_mask(img)
    assert mask is not None
    assert mask.getpixel((0,0)) == 0
    assert mask.getpixel((32,32)) == 255
    # Game sprite PNGs may be indexed, palette-matted images with no alpha.
    indexed = Image.new("P", (64,64), 0)
    indexed.putpalette([152,208,160, 190,30,40] + [0,0,0]*254)
    indexed.paste(1,(12,8,52,59))
    keyed_path = graphics / "trainers" / "back_pics" / "sample.png"
    keyed_path.parent.mkdir(parents=True,exist_ok=True)
    indexed.save(keyed_path)
    with closing(sqlite3.connect(db)) as conn:
        conn.execute("INSERT INTO sprites VALUES(?,?,?,?,?,?,?)",
                     ("b"*24,"trainers/back_pics/sample.png",64,64,1,64,64))
        conn.commit()
    keyed = g.select_frame(graphics,db,{"id":"b"*24,"frame":0})
    assert keyed.getpixel((0,0))[3] == 0, keyed.getpixel((0,0))
    assert keyed.getpixel((25,25)) == (190,30,40,255)
    assert g.reference_alpha_mask(keyed) is not None
    class Fake:
        def __init__(self, cuda=False, mps=False):
            self.cuda = type("FakeCUDA", (), {"is_available": lambda self: cuda})()
            self.backends = type("Backend", (), {
                "mps": type("FakeMPS", (), {"is_available": lambda self: mps})()})()
    assert g.hardware_backend(Fake(cuda=True)) == "cuda"
    assert g.hardware_backend(Fake(mps=True)) == "mps"
    assert g.hardware_backend(Fake()) == "cpu"
    assert len(g.models()) == 2
    assert g.capabilities()["installed"] in (True, False)
print("Canvas local generator preprocessing smoke test passed")
