#!/usr/bin/env python3
"""Create a portable, source-only Canvas AI companion ZIP for any device.

Whitelist-only: no proprietary Pokémon art, user files, caches, GPU weights or
saved model outputs are ever bundled.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
INCLUDED = [
    "index.html",
    "README.md",
    "run_canvas_ai.py",
    "launch_canvas_ai.bat",
    "setup_canvas_ai.bat",
    "launch_canvas_ai.sh",
    "setup_canvas_ai.sh",
    "launch_canvas_references.bat",
    "ai/local_reference_library.py",
    "ai/local_generator.py",
    "ai/requirements-local.txt",
    "docs/LOCAL_IMAGE_AI.md",
    "docs/REFERENCE_LIBRARY.md",
    "docs/AI_STUDIO_ARCHITECTURE.md",
    "ai/contracts/README.md",
    "ai/contracts/reference.schema.json",
    "ai/contracts/training-request.schema.json",
    "ai/contracts/generation-request.schema.json",
]


def package(destination: Path) -> None:
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=8) as z:
        for relative in INCLUDED:
            path = ROOT / relative
            if not path.is_file() or path.is_symlink():
                raise FileNotFoundError(f"Packaging source unavailable: {relative}")
            # Intentionally excludes all .png/.pal files, .venv-ai/, generated
            # images, cache, .git, local model weights, and private databases.
            z.write(path, arcname=relative)
    print(f"Packaged {len(INCLUDED)} clean Canvas AI files: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "dist" / "Canvas-AI-Local-Companion.zip")
    args = parser.parse_args()
    package(args.output)


if __name__ == "__main__":
    main()
