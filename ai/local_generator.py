"""Optional GPU-backed reference-guided sprite generation for locally served Canvas.

No network API or model download occurs until the user explicitly requests Generate.
Reference sprites are loaded from the private indexed PNG library; no training occurs.
"""
from __future__ import annotations

import base64
from contextlib import closing
import io
import os
import random
import threading
import time
import traceback
import uuid
from collections import deque
from pathlib import Path

from PIL import Image

MODEL_IDS = {
    "sd-turbo": "stabilityai/sd-turbo",
    "sd15": "stable-diffusion-v1-5/stable-diffusion-v1-5",
}
MAX_INLINE_BYTES = 3_000_000
RESAMPLING = Image.Resampling.NEAREST
_jobs: dict[str, dict] = {}
_order = deque()
_lock = threading.Lock()
_queue_gate = threading.Lock()
_cache = {}


def capabilities() -> dict:
    try:
        import torch
        gpu = torch.cuda.is_available()
        device = torch.cuda.get_device_name(0) if gpu else "CPU"
        return {"installed": True, "torch": torch.__version__,
                "cuda": gpu, "device": device,
                "model_available": bool(__import__("importlib.util", fromlist=["find_spec"]).find_spec("diffusers"))}
    except (ImportError, OSError) as exc:
        return {"installed": False, "cuda": False, "device": "unavailable",
                "model_available": False, "detail": str(exc)[:180]}


def models() -> list[dict]:
    return [{"id": key, "name": name, "download_on_first_use": True,
             "reference_guided": True, "uses_local_gpu": True}
            for key, name in MODEL_IDS.items()]


def decode_png_data(data: str) -> Image.Image:
    if not isinstance(data, str) or not data.startswith("data:image/png;base64,"):
        raise ValueError("Expected a PNG data URL")
    encoded = data.split(",", 1)[1]
    if len(encoded) > MAX_INLINE_BYTES * 4 // 3 + 16:
        raise ValueError("Uploaded reference is too large")
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > MAX_INLINE_BYTES:
        raise ValueError("Uploaded reference is too large")
    with Image.open(io.BytesIO(raw)) as img:
        img.verify()
    with Image.open(io.BytesIO(raw)) as img:
        if img.width * img.height > 4_194_304:
            raise ValueError("Reference exceeds 4 megapixels")
        return img.convert("RGBA")


def png_data(img: Image.Image) -> str:
    output = io.BytesIO()
    img.save(output, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def select_frame(graphics: Path, db_path: Path, entry: dict) -> Image.Image:
    import sqlite3
    ref_id = entry.get("id", "")
    frame = int(entry.get("frame", 0))
    if not isinstance(ref_id, str) or len(ref_id) != 24 or any(c not in "0123456789abcdef" for c in ref_id):
        raise ValueError("Invalid reference ID")
    with closing(sqlite3.connect(db_path)) as conn:
        row = conn.execute("SELECT relpath,frame_width,frame_height,frame_count,width,height FROM sprites WHERE id=?", (ref_id,)).fetchone()
    if row is None:
        raise ValueError("Reference ID not found")
    rel,fw,fh,count,width,height = row
    if frame < 0 or frame >= count:
        raise ValueError("Reference frame outside sheet")
    source = (graphics / rel).resolve()
    if not any(source.is_relative_to(graphics / d) for d in ("pokemon", "trainers")):
        raise ValueError("Disallowed sprite path")
    with Image.open(source) as img:
        if img.width != width or img.height != height:
            raise ValueError("Reference sheet changed; rescan library")
        columns = max(1, width // fw)
        x,y = (frame % columns) * fw, (frame // columns) * fh
        return img.crop((x,y,x+fw,y+fh)).convert("RGBA")


def subject_crop(image: Image.Image) -> Image.Image:
    """Upscale native pixel art to model resolution with an opaque neutral matte.

    This is image-to-image conditioning, not a trainable IP-Adapter or LoRA.
    """
    source = image.convert("RGBA")
    bounds = source.getchannel("A").getbbox()
    if bounds:
        source = source.crop(bounds)
    # Pixel art is usually 16–80 px. An ordinary thumbnail() never upscales it,
    # leaving a tiny figure in a 512px diffusion input and nearly empty outputs.
    ratio = min(410 / source.width, 410 / source.height)
    source = source.resize((max(1, round(source.width * ratio)),
                            max(1, round(source.height * ratio))), RESAMPLING)
    backdrop = Image.new("RGBA", (512,512), (236,238,242,255))
    backdrop.alpha_composite(source, ((512-source.width)//2,(512-source.height)//2))
    return backdrop.convert("RGB")


def references_montage(images: list[Image.Image]) -> Image.Image:
    if len(images) == 1:
        return subject_crop(images[0])
    backdrop = Image.new("RGB",(512,512),(236,238,242))
    # Main source dominates; supplemental examples occupy a small strip.
    primary = subject_crop(images[0]).resize((512,512), RESAMPLING)
    backdrop.paste(primary)
    w = min(124, 512 // max(1, len(images)-1))
    for i,img in enumerate(images[1:]):
        thumb = subject_crop(img).resize((w,w),RESAMPLING)
        backdrop.paste(thumb,(512 - (len(images)-1-i)*w,512-w))
    return backdrop


def remove_edge_background(img: Image.Image, tolerance: int = 28) -> Image.Image:
    """Remove contiguous near-uniform corner background only, not internal body colors."""
    image = img.convert("RGBA")
    pix = image.load()
    w,h = image.size
    corners = [pix[0,0][:3],pix[w-1,0][:3],pix[0,h-1][:3],pix[w-1,h-1][:3]]
    samples = [sorted(a)[1] for a in zip(*corners)]
    visited = bytearray(w*h)
    queue = deque()
    for x in range(w):
        queue.append((x,0));queue.append((x,h-1))
    for y in range(h):
        queue.append((0,y));queue.append((w-1,y))
    while queue:
        x,y = queue.popleft()
        index = y*w+x
        if visited[index]:
            continue
        visited[index] = 1
        rgb=pix[x,y][:3]
        if max(abs(rgb[k]-samples[k]) for k in range(3)) > tolerance:
            continue
        pix[x,y] = (*rgb,0)
        if x>0: queue.append((x-1,y))
        if x<w-1: queue.append((x+1,y))
        if y>0: queue.append((x,y-1))
        if y<h-1: queue.append((x,y+1))
    return image


def spriteize(image: Image.Image, colors: int = 24) -> Image.Image:
    scaled = image.convert("RGB").resize((64,64),RESAMPLING)
    transparent = remove_edge_background(scaled)
    mask = transparent.getchannel("A")
    palette = transparent.convert("RGB").quantize(colors=max(4,min(48,colors)),dither=Image.Dither.NONE).convert("RGBA")
    palette.putalpha(mask)
    return palette


def load_pipeline(model_key: str, image_to_image: bool):
    import torch
    from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image
    if model_key not in MODEL_IDS:
        raise ValueError("Unsupported local model")
    if not torch.cuda.is_available() and os.environ.get("CANVAS_ALLOW_CPU_AI") != "1":
        raise RuntimeError("CUDA GPU not detected; set CANVAS_ALLOW_CPU_AI=1 for very slow CPU inference")
    name = MODEL_IDS[model_key]
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    base = _cache.get(model_key)
    if base is None:
        base = AutoPipelineForText2Image.from_pretrained(name, torch_dtype=dtype, use_safetensors=True)
        if torch.cuda.is_available():
            base.enable_model_cpu_offload()
        _cache[model_key] = base
    if not image_to_image:
        return base
    composite = _cache.get(model_key+":img2img")
    if composite is None:
        composite = AutoPipelineForImage2Image.from_pipe(base)
        if torch.cuda.is_available():
            composite.enable_model_cpu_offload()
        _cache[model_key+":img2img"] = composite
    return composite


def make_candidates(job: dict, params: dict, graphics: Path, database: Path):
    import torch
    model_key = params.get("model","sd-turbo")
    prompt = params["prompt"].strip()
    if not 3 <= len(prompt) <= 1200:
        raise ValueError("Please enter a description (3–1200 characters)")
    count = params.get("count",1)
    if type(count) is not int or not 1 <= count <= 4:
        raise ValueError("count must be 1–4")
    seed = params.get("seed")
    if seed is None or seed == "":
        seed = random.SystemRandom().randint(0,2**31-1)
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Invalid seed")
    refs = params.get("reference_ids",[])
    uploads = params.get("user_images",[])
    if not isinstance(refs,list) or len(refs)>5 or not isinstance(uploads,list) or len(uploads)>4:
        raise ValueError("At most five indexed references and four uploads")
    images: list[Image.Image] = []
    if params.get("base_image"):
        images.append(decode_png_data(params["base_image"]))
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError("Reference must be an object")
        images.append(select_frame(graphics,database,ref))
    for upload in uploads:
        images.append(decode_png_data(upload))
    job["reference_count"] = len(images)
    job["mode"] = "image-to-image" if images else "text-to-image"
    job["status"] = "loading_model"
    pipeline = load_pipeline(model_key, bool(images))
    job["status"] = "generating"
    guide = 0.0 if model_key=="sd-turbo" else 7.0
    steps = 4 if model_key=="sd-turbo" else 24
    strength = params.get("strength",0.65)
    if not isinstance(strength,(float,int)) or not 0.3 <= strength <= 1.0:
        raise ValueError("strength must be between 0.3 and 1")
    result=[]
    initial = references_montage(images) if images else None
    for i in range(count):
        generator = torch.Generator(device="cpu").manual_seed(seed+i)
        kwargs={"prompt":prompt+", crisp pixel art character sprite, plain neutral background, centered full body",
                "num_inference_steps":steps,"guidance_scale":guide,"generator":generator,
                "height":512,"width":512}
        if images:
            kwargs.pop("height");kwargs.pop("width")
            kwargs["image"]=initial
            kwargs["strength"]=float(strength)
        with torch.inference_mode():
            output = pipeline(**kwargs).images[0]
        sprite = spriteize(output,params.get("colors",24))
        result.append({"seed":seed+i,"image":png_data(sprite),"width":64,"height":64})
        job["progress"]=int((i+1)*100/count)
    job["candidates"]=result
    job["device"]="CUDA" if torch.cuda.is_available() else "CPU"
    job["model_id"]=MODEL_IDS[model_key]
    job["seed"]=seed
    job["status"]="done"


def start_job(params: dict, graphics: Path, database: Path) -> dict:
    if not isinstance(params,dict):
        raise ValueError("Expected request object")
    with _lock:
        active = sum(j["status"] in ("queued","loading_model","generating") for j in _jobs.values())
        if active>=2:
            raise ValueError("Generator is busy; finish the current jobs first")
        job_id=uuid.uuid4().hex
        job={"id":job_id,"created":time.time(),"status":"queued","progress":0,
             "candidates":[],"error":None}
        _jobs[job_id]=job
        _order.append(job_id)
        while len(_order)>12:
            oldest=_order.popleft()
            if _jobs.get(oldest,{}).get("status") in ("done","error"):
                _jobs.pop(oldest,None)
    def worker():
        with _queue_gate:
            try:
                make_candidates(job,params,graphics,database)
            except Exception as exc:
                job["error"]=str(exc)[:350]
                job["status"]="error"
    thread=threading.Thread(target=worker,daemon=True,name="canvas-gen-"+job_id[:6])
    thread.start()
    return {"id":job_id,"status":"queued"}


def job_status(job_id: str) -> dict | None:
    with _lock:
        job=_jobs.get(job_id)
        if not job:
            return None
        return dict(job)
