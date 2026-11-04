# Canvas AI Studio — use the computing power of whoever opens the app

**The local AI is NOT tied to a single developer PC.** Each person runs a private copy on their own device. The static GitHub Pages editor cannot directly launch installed Python or read GPU drivers, so the current implementation provides a **local companion**. This is a genuine generator running on that person's hardware, not a remote AI service.

## Install on each computer

### Windows
1. Obtain a copy of Canvas from [the GitHub repository](https://github.com/Unborne-Fetus/Canvas) or its **Canvas AI Local Companion** workflow ZIP artifact (the package contains source and launchers, *not* the model).
2. Install **Python 3.11 x64** if needed.
3. Double-click `launch_canvas_ai.bat`. On a fresh device it runs `setup_canvas_ai.bat` automatically, which installs an isolated environment in `.venv-ai`. It checks for an NVIDIA GPU before choosing CUDA PyTorch; other Windows PCs use CPU PyTorch.
4. Your browser opens **http://127.0.0.1:8765** on **your device**. No paths or model downloads from the original developer's PC are used.
5. Choose **AI Studio ✦**. The selected model is downloaded into this device's own cache on first generation, with normal license and network requirements.
6. Optionally enter a local Expansion checkout's path in **References ▦ → Index my sprite folder**. Nothing is required here for text-only or personal PNG generation.

### macOS and Linux
1. Install Python 3.11 with `venv` support.
2. In your Canvas copy run `bash setup_canvas_ai.sh`, then `bash launch_canvas_ai.sh` (or `bash launch_canvas_ai.sh /path/to/your/expansion`).
3. The runtime detects CUDA, Apple MPS where available, or CPU. Apple MPS has code support but has not been validated on a Mac; Linux GPU wheel/driver compatibility varies.
4. Use `http://127.0.0.1:8765` in your browser. Backend remains bound to your own loopback address, not the developer's computer.

**No Pokémon asset collection? No problem.** Prompt-only generation, up to four user-uploaded PNGs, and image-to-image from current Canvas art work without an indexed sprite directory. Adding a repository is optional and local to that user's device.

**CPU-only users:** select **Allow slow CPU generation** when prompted, understanding that large diffusion models may require substantial RAM and take much longer. A device does not necessarily meet the model's memory requirements just because the UI can launch.

### What the hosted website can and cannot do
- Public GitHub Pages: drawing and editable `.canvas.json` projects. No silent installation, no direct local filesystem access, no automatic GPU diffusion inference.
- Private per-device companion: serves the editor *and* model API on the same localhost origin. This avoids HTTPS-to-loopback private-network restrictions and doesn't require a central AI server.
- Future browser-only WebGPU mode would need a separate WebGPU-compatible model and memory/performance testing; this **is not implemented**.

## Generate a sprite
1. Open **References ▦**, optionally select up to five frames with **Use for AI**, and/or choose up to four personal PNG references in AI Studio.
2. Open **AI Studio ✦**, describe the creature. Optionally select **Use current Canvas drawing** to guide the model.
3. Generate on **this device** and select **Add as editable layer**. It does not overwrite other layers.

Model weights, reference files, and private uploads are never committed to GitHub. Artwork remains with its original owners; using an indexed PNG as a reference does not automatically grant rights to redistribute or train on it.

## Modes and limitations

- SD-Turbo: quick local inference, typically 4 denoising steps, model ID `stabilityai/sd-turbo`. Fast output is not guaranteed to look like high-quality coherent pixel art.
- Stable Diffusion 1.5: a slower alternative, model ID `stable-diffusion-v1-5/stable-diffusion-v1-5`.
- **Text-only:** generates a new concept from the description.
- **Reference-guided:** uses the current drawing, a selected expansion sprite, or an uploaded PNG as the primary image-to-image initialization; additional selected references appear in a small contact strip. This **does not implement true multi-image attention, IP-Adapter, ControlNet, LoRA, or training**.
- Output: generated 512×512 RGB is reduced to 64×64 with nearest-neighbor pixel sampling, palette quantization, and approximate connected background removal. This is a usability baseline, **not** a dedicated sprite-trained model. Manual pixel cleanup and anatomical corrections will likely be necessary.
- The default 9,703 indexed PNGs remain private local references. The AI does not ingest all assets at once, and **does not train on them**. Selected source frames influence inference only. Training on assets, copying them, or sharing derivative work requires appropriate permissions.
- Frontend remains fully usable without the local AI setup; cloud-hosted GitHub Pages cannot directly access a user's local data or invoke this service. Run the local launcher.

## Security and operating details

- The same-origin Python server binds to localhost. POST and GET requests enforce localhost Host/Origin checks, with strict JSON size limits. No API keys, tokens, proprietary sprite assets, generated images, checkpoints, or downloads are committed to GitHub.
- The model identifier is restricted to two explicit supported names; a user cannot ask the backend to execute arbitrary Python or load an arbitrary local pickle.
- Generated candidates are held in memory (recent jobs only). There is no durable history or retraining until those phases are implemented.
- Downloaded model licenses must be reviewed. Generation is opt-in; no hidden background GPU training.
- If your CUDA GPU is not detected, the backend reports the condition. CPU fallback requires the explicit `CANVAS_ALLOW_CPU_AI=1` environment setting and is likely much slower.
- The `Python 3.11` prerequisite is deliberate: the current globally installed Python 3.14 may lack compatible GPU dependencies.
- Training weights are **not** updated by reference upload or generation.

## Testing

```powershell
node tests/smoke.mjs
node tests/ai-contracts.mjs
python tests/reference-library-smoke.py
python tests/local-generator-smoke.py
```

A full generation smoke test additionally requires a working PyTorch CUDA installation, the chosen Diffusers model downloaded with its license terms accepted, and sufficient GPU memory. The lightweight smoke test deliberately does not download any weights or consume GPU memory.

## Validation on Windows (November 4, 2026)

- PC: NVIDIA GeForce RTX 4060, 8 GB VRAM; isolated Python 3.11 environment; CUDA PyTorch 2.14.1; Diffusers 0.39; SD-Turbo checkpoint cached locally.
- **Verified real generation:** indexed Scizor `anim_front` reference → image-to-image on CUDA → 64×64 RGBA PNG, status `done`, no error.
- **Verified real generation:** original user-provided PNG upload → image-to-image on CUDA → 64×64 PNG, status `done`, no error.
- Indexed GBA sprites such as `scizor/anim_front.png` use a solid palette-index-0 background, not actual PNG transparency; the reference importer now interprets that matte as alpha **without altering the original file**. Reference previews and img2img guides both apply the conversion.
- Fixed a geometry bug where a small input sprite wasn't upscaled to the 512×512 model input (produced nearly empty output). Added a regression test requiring substantial reference coverage.
- **Quality warning:** These are end-to-end functionality checks, not proof of game-ready Scizor anatomy. The generic SD-Turbo output is visibly rough and can include stray pixels or low-fidelity appendages. A curated, permission-cleared, dedicated pixel-art model or fine-tune and interactive pixel cleanup are still needed for polished Pokémon-like sprites.
- **Privacy:** No copyrighted reference PNGs, checkpoint weights, or generated test images were pushed to GitHub.
