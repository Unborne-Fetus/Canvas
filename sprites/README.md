# Canvas sprite projects

Store exported Canvas \`.canvas.json\` files here if you want ChatGPT (using the Canvas Sprite Editor plugin and an authorized GitHub connector) to edit and commit them.

1. In Canvas, click **Edit with AI** (or **Save project**) to download the project.
2. On GitHub, choose **Add file → Upload files** while viewing this folder, and upload the \`.canvas.json\`.
3. Ask ChatGPT: **“Use Canvas Sprite Editor to edit \`sprites/<filename>.canvas.json\`: [describe change]. Commit the edit.”**
4. Download the updated project from GitHub and use **Import** in Canvas.

You can also attach the project file directly to ChatGPT and import the result. That workflow does not require adding the art to GitHub.

### Notes

- The format preserves 64×64 RGBA layers, visibility, opacity, and names.
- Exported PNG files are flattened and cannot restore the original layers.
- The GitHub repository is not a backend for Canvas's browser-local autosave. Editing a GitHub project will not overwrite a browser draft.
- Do not place passwords, API keys, or other secrets in project files.
