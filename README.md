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
