#!/usr/bin/env python3
"""Launch a private Canvas AI instance on the computer running this script.

No specific game repository, account, host IP or GPU is assumed.
"""
from __future__ import annotations

import argparse
import sys
import threading
import webbrowser
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "ai"))
    from local_reference_library import default_db, scan, serve

    parser = argparse.ArgumentParser(description="Canvas AI Studio - private per-device launcher")
    parser.add_argument("--source", type=Path,
                        help="Optional local Pokeemerald Expansion repository to index")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    database = default_db()
    if args.source:
        print("Indexing your chosen local sprite library...", flush=True)
        summary = scan(args.source, database)
        print("Indexed", summary["pokemon"], "Pokémon assets and",
              summary["trainers"], "trainer assets.", flush=True)

    url = f"http://127.0.0.1:{args.port}"
    print(f"Canvas AI is running locally on THIS computer: {url}", flush=True)
    print("You can add a Pokeemerald Expansion folder later in References.", flush=True)
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    serve(database, root, "127.0.0.1", args.port)


if __name__ == "__main__":
    main()
