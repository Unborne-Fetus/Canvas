# AI Live Canvas sprite projects

This directory contains shared `.canvas.json` projects used by **Canvas Sprite Editor**.

**To use AI Live:**

1. Ask ChatGPT's Canvas Sprite Editor to create or update a file such as `sprites/Glowlotl.canvas.json` in `Unborne-Fetus/Canvas`.
2. Open the Canvas editor with `?live=sprites/Glowlotl.canvas.json` appended to its URL, or click **AI Live ✦** and enter that exact path.
3. Keep the page open. When ChatGPT commits a new sprite version to GitHub, the editor checks the public project every ~12 seconds and loads it automatically if it has no local unsynced edits.
4. If you've drawn locally, use **Load update** to accept the AI version and **Restore backup** to revert if necessary.

The site is local-first: drawings you make in the browser are saved only on your device and are **not automatically uploaded to GitHub**. The AI plugin can edit only files accessible through an authorized GitHub connection, not unrelated local browser drafts. For your very first shared project, attach its .canvas.json to ChatGPT (or upload it to this folder). The subsequent AI edits no longer require downloads/imports.

The project format preserves 64×64 RGBA layers, ordering, visibility, opacity, and names. PNG exports are flattened. Do not place passwords, tokens, or secrets in project JSON.
