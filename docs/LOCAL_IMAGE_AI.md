# Local AI Studio — working V1 architecture and operating instructions

**Purpose:** Generate 64×64 sprite candidates on the user's PC with an optional GPU model, using a text prompt and selected Pokémon/trainer or uploaded references.

## Starting on Windows

1. Clone or update `Unborne-Fetus/Canvas` on your PC.
2. Run `setup_canvas_ai.bat` **once**. It creates an isolated Python 3.11 environment and installs CUDA-enabled PyTorch and Diffusers. A compatible NVIDIA GPU is strongly recommended.
3. Run `launch_canvas_ai.bat` to index the existing local Pokeemerald Expansion / Brisk Emerald PNGs, serve Canvas at **http://127.0.0.1:8765**, and activate the local AI interface.
4. Open **References ▦** and choose **Use for AI** on up to five frames from the indexed Pokémon/trainer sheets. You can also add up to four personal PNG references in the AI Studio dialog.
5. Click **AI Studio ✦**, enter a description and select Generate. Choose the optional **Use current Canvas drawing as the main reference** checkbox to use existing editable artwork as image-to-image initialization.
6. Select a generated candidate and choose **Add as editable layer**. Your original drawing and layer stack are preserved. You can undo the insertion.

The model is downloaded *only* when a user explicitly clicks Generate. Model downloads can be several gigabytes and depend on network availability and model license/access. Models stay in your own cache, **not Git**.

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
