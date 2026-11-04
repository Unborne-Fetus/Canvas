# Canvas — Fakémon Sprite Studio

A free, local-first, 64×64 pixel-art editor built for drawing custom monster sprites and Fakémon. No framework, backend, or account required.

## Features

- Fixed 64×64 transparent pixel canvas, zoom from 300% to 2400%, optional grid, live 1:1 preview
- Pencil, eraser, flood fill, eyedropper, line, outline/filled rectangle, outline/filled ellipse
- Adjustable brush sizes (1–12 pixels), horizontal and vertical mirror drawing, right-click to erase
- Rectangular selection, copy, cut, and paste
- Multi-layer editing (up to 24 layers): visibility, opacity, duplicate, rename, reorder, delete
- 72+ spectrum colors, retro 32-color set, pastels, natural tones, and custom swatches
- Primary and secondary colors, native color picker, HEX field, undo/redo (40 steps)
- Export native 64×64 transparent PNG or enlarged 512×512 PNG (nearest-neighbor)
- Import PNG and other browser-readable images as layers; aspect-ratio preserving fit to 64×64
- Save and reopen editable .canvas.json projects, including all layers
- Autosave to local browser storage; no images are uploaded to a server
- Touch/pointer drawing, mobile-responsive layout, keyboard shortcuts

## Use it

### In the browser

If GitHub Pages is enabled, the site is deployed automatically whenever changes are pushed to the main branch.

To enable the site:
1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Open **Actions** and run the **Test and deploy Canvas** workflow if necessary.
4. The Pages settings will display the site address after a successful deployment.

**Note:** GitHub Pages availability for a private repository depends on your GitHub plan. You can leave the repository private and run it locally even if Pages isn't available.

### Without a server

Download or clone the repository and open **index.html** in Chrome, Edge, Firefox, or Safari. The app contains no CDN assets or external dependencies.

You can also serve the directory using Python:

    python -m http.server 8000

Then visit http://localhost:8000.

## Basic controls

| Action | Shortcut |
| --- | --- |
| Pencil / Eraser / Fill / Pick | B / E / G / I |
| Line / Rectangle / Ellipse | L / R / O |
| Filled rectangle / ellipse | Shift+R / Shift+O |
| Selection | M |
| Swap colors | X |
| Brush size | [ / ] |
| Erase temporarily | Right mouse button |
| Pan viewport | Hold Space and drag |
| Undo / Redo | Ctrl+Z / Ctrl+Y |
| Save project / Open | Ctrl+S / Ctrl+O |
| Copy / Cut / Paste selection | Ctrl+C / Ctrl+X / Ctrl+V |
| Clear selection | Escape |

On macOS, use Command instead of Ctrl.


## Canvas AI Studio (design in progress)

The implementation blueprint for a **real trained 64×64 sprite AI**, a user-expandable reference library, model training, and non-destructive editor integration is in [Canvas AI Studio architecture](docs/AI_STUDIO_ARCHITECTURE.md). The [machine-readable API contracts](ai/contracts/README.md) and [contract smoke tests](tests/ai-contracts.mjs) are also committed.

**Current status:** design and contracts are in place. The trained model, training service, reference importer, AI Studio interface, and in-app generation are **not implemented yet**. The present **AI Live ✦** feature below is a separate GitHub-backed ChatGPT sync mechanism.

The planned importer can discover sprites in a local Pokeemerald Expansion asset collection, but artwork is not bundled or automatically authorized for redistribution/training; each training dataset must have verified permissions.

## Pokémon and trainer reference library (local)

Canvas now includes a **References ▦** browser when launched with its local Python companion. A recursive importer indexes all PNG sheets under both `graphics/pokemon` and `graphics/trainers` from an existing Pokeemerald Expansion/Brisk Emerald checkout **without copying artwork to this public repository**. Search species/trainers, browse frames of sprite sheets, and click **Add frame** to add a non-destructive editable Canvas layer.

For Windows, clone this repo locally and run **`launch_canvas_references.bat`**. The default source is `C:\ROM Hacks\Pokemon Brisk Emerald`; pass a different source repository path as the first argument if needed. Then open **http://127.0.0.1:8765** (not the GitHub Pages site) to browse locally indexed sprites. See [Reference Library Guide](docs/REFERENCE_LIBRARY.md).

**No actual AI model training is performed during import.** Permissions for model training remain unreviewed and disabled by default because Pokémon and community sprites have different rights holders.

## AI Studio: local PC image generation (V1)

Canvas now has an optional **AI Studio ✦** dialog for GPU-backed 64×64 image generation, **without a paid API**. The optional local service uses the user's own computer, supports a text prompt, selected expansion references from **References ▦**, up to four user-uploaded PNGs, and current Canvas pixels as an image-to-image starting point. Results can be inserted as **new undoable editable layers**.

**On Windows:** run `setup_canvas_ai.bat` once (installs Python 3.11 CUDA PyTorch and Diffusers), then run `launch_canvas_ai.bat` to open `http://127.0.0.1:8765`. The selected pretrained model downloads only on the first Generate click. Learn about limitations, privacy, optional models, and setup in [Local Image AI Guide](docs/LOCAL_IMAGE_AI.md).

The V1 model is a general pretrained diffusion model, **not** a Pokémon-trained model. References serve as input images (with an optional contact strip), **not fine-tuning data**. Outputs will require quality review. No proprietary Pokémon artwork, model weights, or user uploads are published to this repo.

## AI Live editing with ChatGPT

Canvas supports **GitHub-backed AI Live** mode for sprites in this public repository. You no longer need to download or import a project every time ChatGPT edits it.

1. Ask **Canvas Sprite Editor** to create or update a `sprites/NAME.canvas.json` project in `Unborne-Fetus/Canvas`.
2. Open Canvas with `?live=sprites/NAME.canvas.json` appended to the editor URL. Alternatively, click **AI Live ✦**, enter the GitHub path, and connect.
3. Leave the tab open. When ChatGPT edits the project and commits it to GitHub, Canvas checks for a new revision approximately every 12 seconds while the tab is visible.
4. Use **Copy AI prompt** for the exact path to request further changes in ChatGPT. If you have drawn on the canvas since connecting, click **Load update** to accept the incoming AI revision (a local backup is saved first). Use **Restore backup** to recover the previous browser draft.

**Important limitations:** This is a read-only GitHub-to-browser sync from ChatGPT's authenticated GitHub commits, **not** browser-to-GitHub real-time collaboration. Strokes made in the browser remain autosaved on that device; ChatGPT cannot see them until they are shared in the GitHub sprite file. It never asks for GitHub passwords or tokens. It works with public GitHub sprite files and needs the Pages site or another hosting option to be available. Network caching and deployment may introduce delay; it is not an instant shared drawing surface.

For a draft that exists only in your browser, one initial export/upload or chat attachment is still needed to establish the GitHub-backed sprite. After it exists in `sprites/`, subsequent edits can flow directly from ChatGPT to the open Canvas page.

### Polished sprite tools

- **Outline 1px** adds an outline around opaque pixels on the active layer in the primary color.
- **Recolor** replaces the secondary RGB color with the primary RGB color on the active layer.
- Click the project name to rename it.
- **Ctrl+A** selects the whole sprite; **Delete** clears pixels in the selected area.
- **Alt+click** samples a color from the canvas without switching tools.

## Image and project formats

- **Export PNG**: 64×64 RGBA, no background burned into the image. This is the sprite size intended for use in Pokémon-inspired fan projects.
- **Export ×8 preview PNG**: 512×512 RGBA with crisp pixel edges.
- **Save project**: versioned JSON with base64-encoded RGBA buffers for every layer. Use Import to reopen it.
- **Import image**: scaled to fit a 64×64 layer without smoothing. For best results, import a 64×64 transparent PNG.

All browser autosaves remain on the user's own device. Export a project file to back up your work before clearing browser data or changing browsers.

## Development

This is a deliberately simple, dependency-free static website. The complete editor lives in index.html.

Run a basic static smoke test (requires Node.js):

    node tests/smoke.mjs

The GitHub Actions workflow tests the HTML/JavaScript and publishes the static page when Pages is configured.

## License and rights

Artists own the artwork they create with Canvas. Canvas doesn't include Pokémon game assets, sprites, or proprietary art. If publishing a Fakémon game or distributing sprites derived from another artist's work, ensure you have permission for any assets you use.
