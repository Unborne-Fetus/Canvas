# Pokémon and trainer reference library

**Status:** implemented local bulk import, browsing, frame inspection, and **Add frame as layer**. **Not** model training.

The importer indexes PNG sprite files under an existing Pokeemerald Expansion/Brisk Emerald checkout and serves them privately from the user's own machine. It does **not** upload the source artwork or copy it into the public Canvas repository.

## Per-user setup

References belong to **whoever is running Canvas**, not a single development computer.

1. Obtain Canvas on your computer.
2. Start the local companion using `launch_canvas_ai.bat` (Windows) or `bash launch_canvas_ai.sh` (macOS/Linux). On Windows, it installs the optional local model environment on first launch; Python 3.11 is required.
3. Open **http://127.0.0.1:8765** on that computer and choose **References ▦**.
4. Enter the path to **your own** Pokeemerald Expansion repository and click **Index my sprite folder**. The browser cannot pick arbitrary directories from a website, so provide an existing path to a locally accessible checkout. A path is optional.
5. Search and browse indexed Pokémon and trainer sheets. Choose **Add frame** to insert one as a layer, or **Use for AI** for image-to-image guidance.

For a reference-only launch without the large AI model dependencies, Python and Pillow are enough: run `python ai/local_reference_library.py serve --site .` and use the in-app import field. Alternatively run `python ai/local_reference_library.py scan --source "/path/to/your/expansion"` before serving.

The static GitHub Pages site does not have access to the visitor's private files. Use the local URL to browse personal sprite collections. No source image is copied into the public repo.

## What gets indexed

- Every valid PNG under `graphics/pokemon` and `graphics/trainers`, recursively, including front sprites, animation sheets, back sprites, icons, footprints, overworld sprite strips, trainer portraits, and back sprites.
- Original paths are retained in a private SQLite catalog with content SHA-256 hashes, dimensions, inferred square frame dimensions and frame counts.
- Every file counts once, regardless of frames. Frame counts are **best-effort inferences** based on 16/32/64/80 pixel grid patterns; manually inspect atypical sheets.
- Supporting `.pal` palette files remain in the source repository. The importer does not treat `.pal` files as sprite images or include them in its image count.
- On re-scan, changed files are reindexed and removed source files are dropped. The source art is never modified.
- SQLite database defaults to `%LOCALAPPDATA%\CanvasAI\references.sqlite3` on Windows (or `~/.local/share/CanvasAI/references.sqlite3` on Linux/macOS).

## Security and permissions

The private companion binds only to `127.0.0.1` by default, serves the editor and read-only catalog endpoints on the same origin, and never accepts uploads or exposes arbitrary filesystem paths. Only catalogued PNGs inside the two approved source directories can be fetched. The browser references are not published to GitHub and the service should never be forwarded to the public internet.

**Art rights:** Pokeemerald Expansion and Brisk Emerald include official and community art by multiple rights holders. Local cataloguing is separate from permission to *train* an AI or redistribute sprites. The importer leaves training permissions **unreviewed and disabled for all**. An explicitly rights-cleared training dataset is required before model training.

## Tests

```bash
node tests/smoke.mjs
python tests/reference-library-smoke.py
node tests/ai-contracts.mjs
```

The Python fixture test uses synthetic original RGBA PNGs; no third-party art is included.

## What's next

- Associate palette files and creator credits with catalog entries.
- Add an explicit permission review process for eligible training datasets.
- Provide selectable image sheets and masks to the future conditional model.
- Implement the separate GPU training service and real model inference, as described in [AI Studio Architecture](AI_STUDIO_ARCHITECTURE.md).
