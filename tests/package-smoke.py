#!/usr/bin/env python3
"""Ensure a portable Canvas ZIP contains only whitelisted public app files."""
import tempfile
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from package_canvas_ai import package, INCLUDED

with tempfile.TemporaryDirectory() as temp:
    path=Path(temp)/"Canvas-AI-Local-Companion.zip"
    package(path)
    with ZipFile(path) as z:
        assert set(z.namelist())==set(INCLUDED)
        assert z.testzip() is None
        assert all(not n.endswith((".png",".pal",".db",".sqlite3",".safetensors",".pth")) for n in z.namelist())
        assert "index.html" in z.namelist()
        assert "ai/local_reference_library.py" in z.namelist()
        assert "run_canvas_ai.py" in z.namelist()
print("Portable Canvas AI packaging smoke test passed")
