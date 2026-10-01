#!/usr/bin/env python3
"""
Unique featured image per Kitchen Tales post.

The real product photo is cut out from its white studio background and pasted,
pixel-for-pixel (only uniformly scaled), onto a freshly generated background
scene in The Pickle Affair brand palette. The jar's colour, shape, label and
packaging are never redrawn or recoloured — only the scene around it is new.

Background providers (BLOG_IMAGE_PROVIDER):
  auto       — library first, then any configured AI provider (Cloudflare, OpenAI), else local (default)
  library    — curated photoreal scenes in scratch/backgrounds/, matched to the topic (no API needed)
  cloudflare — Cloudflare Workers AI FLUX.2 klein, falling back to FLUX.1 schnell
               (CLOUDFLARE_ACCOUNT_ID + CLOUDFLARE_API_TOKEN; free daily tier; CLOUDFLARE_IMAGE_MODEL overrides)
  openai     — OpenAI image model (OPENAI_API_KEY)
  local      — procedural brand-palette scene, seeded per topic (no API needed)
  off        — skip generation; caller keeps the raw product photo
Any AI failure falls back to the next provider and finally to local.

CLI preview:
  python3 scratch/blog_image.py <topic_id> [--out preview.jpg] [--provider cloudflare]
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import io
import json
import math
import os
import random
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = {p["handle"]: p for p in json.loads((ROOT / "scratch" / "product_registry.json").read_text())}
CACHE_DIR = ROOT / "scratch" / ".cache" / "cutouts"
CTX = ssl.create_default_context()

W, H = 1600, 900

BRAND = {
    "leaf": (74, 107, 41),       # #4A6B29
    "olive": (47, 74, 26),       # #2F4A1A
    "ink": (29, 38, 20),         # #1D2614
    "cream": (251, 246, 234),    # #FBF6EA
    "ivory": (245, 247, 240),    # #F5F7F0
    "sage": (221, 229, 200),     # #DDE5C8
    "mango": (232, 163, 61),     # #E8A33D
    "turmeric": (217, 154, 30),  # #D99A1E
    "terracotta": (181, 83, 42), # #B5532A
    "chilli": (192, 57, 43),     # #C0392B
    "wood": (168, 107, 60),      # #A86B3C
}

# Scene wording avoids containers (pantry, pots, vessels): FLUX ignores "no jars" and
# happily adds extra jars next to the real product when a scene suggests storage.
ANGLE_SCENES = {
    "storage": "a clean, airy Indian kitchen countertop in soft morning light, a dry steel spoon resting on a folded cotton cloth, a wooden chopping board, cool shaded corner",
    "shelf_life": "a calm sunlit Gujarati kitchen corner with carved wooden panels, a steel spoon on a cotton napkin, a sprig of curry leaves",
    "ingredient": "a rustic wooden board scattered with whole spices — mustard seeds, fenugreek seeds, dried red chillies, turmeric and rock salt in small brass katoris",
    "pairing": "a Gujarati meal — thepla, khichdi and a cup of masala chai on small brass plates — placed toward the edges of the table",
    "comparison": "a balanced, symmetrical wooden tabletop with two small brass bowls placed far left and far right, raw mango slices and jaggery pieces",
    "baa_story": "a warm traditional Kathiawadi home kitchen with brass plates, a wooden rolling pin and a clay diya, sunlight streaming through a carved jharokha window",
    "buying": "a festive gifting table with jute cloth, marigold flowers, a kraft paper gift box and twine in warm light",
    "heritage_product": "a sun-drenched Kathiawadi courtyard table with raw green mangoes, mango leaves, brass katoris of spices, terracotta and jute textures",
    "pillar_overview": "a generous Gujarati festive spread on a wooden table with raw mangoes, mango leaves, brass katoris of spices and marigold flowers",
}
DEFAULT_SCENE = ANGLE_SCENES["heritage_product"]

PALETTES = [
    # (wall_top, wall_bottom, glow, table_top, table_bottom, leaf, accent)
    ((251, 246, 234), (241, 228, 200), (242, 196, 107), (196, 142, 88), (158, 101, 58), BRAND["leaf"], BRAND["chilli"]),
    ((245, 247, 240), (221, 229, 200), (236, 214, 150), (120, 146, 80), (74, 107, 41), BRAND["olive"], BRAND["mango"]),
    ((252, 240, 220), (240, 206, 160), (246, 180, 90), (181, 110, 70), (140, 70, 40), BRAND["leaf"], BRAND["turmeric"]),
    ((250, 244, 228), (232, 222, 190), (230, 190, 120), (150, 120, 80), (110, 84, 52), BRAND["leaf"], BRAND["terracotta"]),
]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def _seed(*parts: str) -> int:
    return int(hashlib.sha1("|".join(parts).encode()).hexdigest()[:8], 16)


def _download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "PickleAffairBlogImage/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as resp:
        return resp.read()


# ---------------------------------------------------------------- product cutout

def _edge_connected(candidate: np.ndarray) -> np.ndarray:
    """Pixels of `candidate` connected to the image border."""
    # .copy(): array-backed images are not mutated in place by floodfill.
    mask = Image.fromarray(np.pad(candidate, 1, constant_values=True).astype(np.uint8) * 255).copy()
    ImageDraw.floodfill(mask, (0, 0), 128)
    return np.asarray(mask)[1:-1, 1:-1] == 128


def cutout_product(img: Image.Image) -> Image.Image:
    """Remove the white studio background; product pixels stay exactly as shot.

    Only near-white, low-saturation pixels connected to the image border are
    treated as background. Light-grey studio shadow becomes a soft
    semi-transparent shadow instead of a grey blob.
    """
    rgb = img.convert("RGB")
    a = np.asarray(rgb).astype(np.int16)
    mn = a.min(axis=2)
    mx = a.max(axis=2)
    candidate = (mn >= 196) & ((mx - mn) <= 24)
    bg = _edge_connected(candidate)

    # The glass base reflects a pale pink/lavender tint onto the white sweep. Allow that
    # looser tint only in the strip under the jar so warm lid/label highlights are never touched.
    ys = np.where(~bg.all(axis=1))[0]
    if ys.size:
        strip_top = ys.max() - int((ys.max() - ys.min()) * 0.07)
        r, b = a[..., 0], a[..., 2]
        loose = (mn >= 165) & ((mx - mn) <= 60) & ((r - b) <= 50)
        loose[:strip_top] = False
        bg = _edge_connected(bg | loose)

    lum = a.mean(axis=2)
    shadow_alpha = np.clip((250.0 - lum) / 54.0, 0.0, 1.0) * 120.0
    alpha = np.where(bg, shadow_alpha, 255.0)

    # Defringe: product pixels touching the background that are mostly white are
    # anti-aliasing blend with the studio sweep, not product.
    ring = np.asarray(Image.fromarray(bg.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(3))) > 0
    ring &= ~bg
    alpha = np.where(ring, np.clip((255.0 - mn) / 105.0, 0.0, 1.0) * 255.0, alpha).astype(np.uint8)

    out = np.dstack([np.asarray(rgb), alpha])
    shadow_rgb = np.array([45, 32, 20], dtype=np.uint8)
    out[bg, :3] = shadow_rgb

    cut = Image.fromarray(out)
    bbox = Image.fromarray((alpha > 10).astype(np.uint8) * 255).getbbox()
    return cut.crop(bbox) if bbox else cut


def product_cutout(handle: str) -> Image.Image:
    p = PRODUCTS[handle]
    url = p["image"]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f"{_slug(handle)[:50]}-{hashlib.sha1(url.encode()).hexdigest()[:10]}.png"
    if cache.exists():
        return Image.open(cache).convert("RGBA")
    cut = cutout_product(Image.open(io.BytesIO(_download(url))))
    cut.save(cache)
    return cut


# ---------------------------------------------------------------- backgrounds

def _props_for(handles: list[str]) -> str:
    props = [PRODUCTS[h].get("scene_props", "") for h in handles if h in PRODUCTS]
    return "; ".join(p for p in props if p) or "raw green mangoes and mango leaves"


def build_prompt(topic: dict, handles: list[str]) -> str:
    scene = ANGLE_SCENES.get(topic.get("angle", ""), DEFAULT_SCENE)
    return (
        "Photorealistic premium food-photography background plate for The Pickle Affair, "
        "a handcrafted Kathiawadi (Gujarat) pickle brand. "
        f"Blog theme: {topic.get('primary_keyword') or topic.get('title', '')}. "
        f"Scene: {scene}. "
        f"Ingredient props that match the pickle: {_props_for(handles)}. "
        "Brand look: warm cream and ivory base, leaf green (#4A6B29) and deep olive accents, "
        "ripe mango yellow, turmeric and terracotta highlights, brass, jute and wood textures, "
        "natural soft daylight from the left, gentle shallow depth of field. "
        "Composition: wide 16:9 landscape, camera at eye level with the tabletop; the tabletop fills "
        "the lower third; keep the CENTRAL 50% of the frame completely empty — a clear tabletop with a "
        "softly blurred background — because product jars will be composited there later; place props "
        "only near the left and right edges. "
        "Strictly no jars, bottles, labelled containers, packaging, text, letters, numbers, logos, "
        "watermarks, hands or people."
    )


CF_FLUX2 = "@cf/black-forest-labs/flux-2-klein-4b"
CF_FLUX1 = "@cf/black-forest-labs/flux-1-schnell"


def _multipart(fields: dict) -> tuple[bytes, str]:
    boundary = f"----tpa{random.getrandbits(64):016x}"
    body = b"".join(
        f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
        for k, v in fields.items()
    ) + f"--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def _cloudflare_run(model: str, prompt: str, seed: int) -> Image.Image:
    account = os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
    token = os.environ["CLOUDFLARE_API_TOKEN"].strip()
    if "flux-2" in model:
        # FLUX.2 takes multipart form data and renders 16:9 natively (steps are fixed on klein).
        body, ctype = _multipart({"prompt": prompt[:2048], "width": 1536, "height": 864, "seed": seed})
    else:
        # flux-1-schnell's schema rejects any field besides prompt/steps (including seed).
        body, ctype = json.dumps({"prompt": prompt[:2048], "steps": 8}).encode(), "application/json"
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{model}",
        data=body,
        method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": ctype},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=180) as resp:
            raw = resp.read()
            rtype = resp.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Cloudflare AI {model} {e.code}: {e.read().decode()[:300]}") from e
    if rtype.startswith("image/"):
        return Image.open(io.BytesIO(raw)).convert("RGB")
    data = json.loads(raw.decode())
    image_b64 = (data.get("result") or {}).get("image")
    if not data.get("success", True) or not image_b64:
        raise RuntimeError(f"Cloudflare AI {model} returned no image: {str(data.get('errors'))[:300]}")
    return Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB")


def cloudflare_background(prompt: str, seed: int = 0) -> Image.Image:
    """FLUX.2 klein (sharper, native 16:9, ~160 neurons) with FLUX.1 schnell as fallback."""
    if not (os.environ.get("CLOUDFLARE_ACCOUNT_ID") and os.environ.get("CLOUDFLARE_API_TOKEN")):
        raise RuntimeError("CLOUDFLARE_ACCOUNT_ID / CLOUDFLARE_API_TOKEN not set")
    preferred = os.environ.get("CLOUDFLARE_IMAGE_MODEL", "").strip() or CF_FLUX2
    errors = []
    for model in dict.fromkeys([preferred, CF_FLUX1]):
        try:
            return _cloudflare_run(model, prompt, seed)
        except Exception as e:  # noqa: BLE001 — try the next model
            errors.append(str(e))
            print(f"[blog_image] {e}", file=sys.stderr)
    raise RuntimeError(" | ".join(errors))


def build_flux_prompt(topic: dict, handles: list[str]) -> str:
    """Short, positive-only wording: FLUX drops negations and drifts to overhead food shots."""
    scene = ANGLE_SCENES.get(topic.get("angle", ""), DEFAULT_SCENE)
    return (
        "High-end commercial food advertising photograph, side view at table height, "
        "eye-level straight-on camera, 85mm lens, the front edge of a warm wooden tabletop in the lower third. "
        f"Setting: {scene}. "
        f"Small styled props only near the far left and far right edges: {_props_for(handles)}. "
        "The middle of the tabletop is clear and empty, with a bright, softly blurred background behind it "
        "and creamy bokeh. "
        "Warm cream and ivory tones with leaf green, ripe mango yellow, turmeric and terracotta accents, "
        "brass, jute and wood textures, soft golden morning daylight from the left, airy and bright, "
        "shallow depth of field, photorealistic, premium handcrafted Gujarati food brand."
    )


def openai_background(prompt: str) -> Image.Image:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    model = os.environ.get("BLOG_IMAGE_MODEL", "gpt-image-1")
    payload: dict = {"model": model, "prompt": prompt, "n": 1}
    if model.startswith("dall-e"):
        payload.update(size="1792x1024", response_format="b64_json", quality="hd")
    else:
        payload.update(size="1536x1024", quality=os.environ.get("BLOG_IMAGE_QUALITY", "medium"))
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=240) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenAI image API {e.code}: {e.read().decode()[:300]}") from e
    item = data["data"][0]
    raw = base64.b64decode(item["b64_json"]) if item.get("b64_json") else _download(item["url"])
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _vgradient(size: tuple[int, int], top: tuple, bottom: tuple) -> Image.Image:
    w, h = size
    t = np.linspace(0.0, 1.0, h)[:, None, None]
    grad = np.array(top)[None, None, :] * (1 - t) + np.array(bottom)[None, None, :] * t
    return Image.fromarray(np.repeat(grad, w, axis=1).astype(np.uint8))


def _leaf(length: int, color: tuple, angle: float) -> Image.Image:
    wdt = max(8, int(length * 0.38))
    layer = Image.new("RGBA", (length, wdt), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([0, 0, length - 1, wdt - 1], fill=color + (235,))
    vein = tuple(min(255, c + 45) for c in color)
    d.line([(length * 0.06, wdt / 2), (length * 0.94, wdt / 2)], fill=vein + (200,), width=max(1, wdt // 12))
    return layer.rotate(angle, expand=True, resample=Image.BICUBIC)


def _texture(size: tuple[int, int], nprng: np.random.Generator, streak: float, fine: float) -> np.ndarray:
    """Multiplicative texture: horizontal wood-grain streaks plus fine plaster noise."""
    w, h = size
    coarse = nprng.normal(0.0, 1.0, (h, max(4, w // 90))).astype(np.float32)
    streaks = np.asarray(Image.fromarray(coarse).resize((w, h), Image.BICUBIC))
    grain = nprng.normal(0.0, 1.0, (h, w)).astype(np.float32)
    return 1.0 + streak * streaks + fine * grain


def _leaf_layer(rng: random.Random, leaf: tuple, horizon: int, count: int, size: tuple[int, int], blur: int) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for side in (0, 1):
        for _ in range(count):
            length = rng.randint(*size)
            shade = tuple(max(0, min(255, c + rng.randint(-22, 18))) for c in leaf)
            lf = _leaf(length, shade, rng.uniform(-65, 65) + (180 if side else 0))
            x = rng.randint(-lf.width // 2, 200) if side == 0 else rng.randint(W - 200 - lf.width // 2, W - lf.width // 3)
            y = rng.randint(-lf.height // 2, int(horizon * 0.5))
            layer.alpha_composite(lf, (x, y))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def local_background(topic: dict) -> Image.Image:
    """Brand-palette scene; layout and palette vary per topic so no two posts match."""
    rng = random.Random(_seed(topic.get("id", ""), topic.get("title", "")))
    nprng = np.random.default_rng(rng.randrange(2**32))
    wall_t, wall_b, glow, tab_t, tab_b, leaf, accent = PALETTES[rng.randrange(len(PALETTES))]
    horizon = int(H * rng.uniform(0.60, 0.68))

    wall = np.asarray(_vgradient((W, horizon), wall_t, wall_b)).astype(np.float32)
    wall *= _texture((W, horizon), nprng, 0.0, 0.012)[..., None]
    table = np.asarray(_vgradient((W, H - horizon), tab_t, tab_b)).astype(np.float32)
    table *= _texture((W, H - horizon), nprng, 0.07, 0.02)[..., None]
    bg = Image.fromarray(np.clip(np.vstack([wall, table]), 0, 255).astype(np.uint8)).convert("RGBA")

    # Soft glow behind the product area plus a diagonal window-light beam.
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light)
    cx, cy = W // 2 + rng.randint(-60, 60), int(horizon * 0.62)
    r = int(H * rng.uniform(0.42, 0.55))
    ld.ellipse([cx - r * 1.4, cy - r, cx + r * 1.4, cy + r], fill=glow + (140,))
    bx = rng.randint(int(W * 0.1), int(W * 0.35))
    ld.polygon([(bx, 0), (bx + 260, 0), (bx + 760, horizon), (bx + 380, horizon)], fill=(255, 250, 235, 70))
    bg = Image.alpha_composite(bg, light.filter(ImageFilter.GaussianBlur(110)))

    # Out-of-focus bokeh on the wall.
    bokeh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bokeh)
    for _ in range(rng.randint(8, 14)):
        rad = rng.randint(18, 60)
        x = rng.choice([rng.randint(0, int(W * 0.3)), rng.randint(int(W * 0.7), W)])
        y = rng.randint(0, int(horizon * 0.8))
        bd.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(255, 248, 225, rng.randint(30, 60)))
    bg = Image.alpha_composite(bg, bokeh.filter(ImageFilter.GaussianBlur(5)))

    # Table-edge highlight for depth.
    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rectangle([0, horizon - 2, W, horizon + 3], fill=(255, 255, 255, 60))
    bg = Image.alpha_composite(bg, edge.filter(ImageFilter.GaussianBlur(2)))

    # Mango leaves: a soft background layer and a very blurred foreground layer at the corners.
    bg = Image.alpha_composite(bg, _leaf_layer(rng, leaf, horizon, rng.randint(2, 4), (160, 260), 9))
    dark_leaf = tuple(int(c * 0.7) for c in leaf)
    bg = Image.alpha_composite(bg, _leaf_layer(rng, dark_leaf, horizon, rng.randint(1, 2), (300, 440), 18))

    # Whole spices scattered on the table, kept to the edges.
    spices = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(spices)
    seed_colors = [(60, 40, 25), (35, 28, 20), accent, BRAND["mango"], (205, 160, 60)]
    for _ in range(rng.randint(70, 130)):
        x = rng.choice([rng.randint(30, int(W * 0.26)), rng.randint(int(W * 0.74), W - 30)])
        y = rng.randint(horizon + 25, H - 15)
        rad = rng.choice([3, 4, 5, 6, 9])
        col = rng.choice(seed_colors)
        sd.ellipse([x - rad, y - rad * 0.8, x + rad, y + rad * 0.8], fill=col + (230,))
    bg = Image.alpha_composite(bg, spices.filter(ImageFilter.GaussianBlur(1.5)))

    # Gentle vignette keeps attention on the jar.
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vig = (np.clip(dist - 0.55, 0, 1) * 110).astype(np.uint8)
    vignette = Image.fromarray(np.dstack([np.full((H, W, 3), 40, np.uint8), vig]))
    return Image.alpha_composite(bg, vignette).convert("RGB")


BG_DIR = ROOT / "scratch" / "backgrounds"
# Curated scenes (no jars, text or people) with the tabletop height where a jar stands.
BG_BASE = {
    "buying-1": 0.90, "buying-2": 0.92, "buying-3": 0.92,
    "comparison-1": 0.92, "comparison-2": 0.86,
    "festive-1": 0.92,
    "heritage-1": 0.84, "heritage-2": 0.77, "heritage-3": 0.90,
    "ingredient-1": 0.87, "ingredient-2": 0.92, "ingredient-3": 0.85,
    "pairing-1": 0.89, "pairing-3": 0.89, "pairing-4": 0.89,
    "storage-1": 0.92, "storage-2": 0.92,
}
BG_BY_ANGLE = {
    "ingredient": ["ingredient-1", "ingredient-2", "ingredient-3", "comparison-1"],
    "pairing": ["pairing-1", "pairing-3", "pairing-4"],
    "storage": ["storage-1", "storage-2", "buying-2"],
    "shelf_life": ["storage-1", "storage-2", "buying-2"],
    "comparison": ["comparison-1", "comparison-2", "ingredient-3"],
    "buying": ["buying-1", "buying-2", "buying-3"],
    "baa_story": ["heritage-1", "heritage-2", "heritage-3"],
    "heritage_product": ["heritage-1", "heritage-2", "heritage-3", "ingredient-1"],
    "pillar_overview": ["heritage-1", "heritage-2", "heritage-3"],
}
BG_BY_KEYWORD = [
    (("gift", "diwali", "festive", "hamper", "corporate"), ["festive-1"]),
    (("monsoon", "rain"), ["storage-2"]),
    (("sun dried", "sun-dried", "sun drying", "season"), ["heritage-3"]),
]


def library_background(topic: dict) -> tuple[Image.Image, float, bool]:
    """Pick a curated scene for the topic; rotates daily and mirrors some for variety.

    Returns (image, jar base height, light comes from the left)."""
    text = f"{topic.get('primary_keyword', '')} {topic.get('title', '')}".lower()
    names = next((n for keys, n in BG_BY_KEYWORD if any(k in text for k in keys)), None)
    names = names or BG_BY_ANGLE.get(topic.get("angle", ""), list(BG_BASE))
    names = [n for n in names if (BG_DIR / f"{n}.jpg").exists()]
    if not names:
        raise RuntimeError("background library is empty")
    seed = _seed(topic.get("id", ""), topic.get("title", ""))
    name = names[(dt.date.today().toordinal() + seed) % len(names)]
    img = Image.open(BG_DIR / f"{name}.jpg").convert("RGB")
    light_left = not (seed >> 5) & 1
    if not light_left:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img, BG_BASE.get(name, 0.92), light_left


def _cover(img: Image.Image, size: tuple[int, int], y_bias: float = 0.5) -> Image.Image:
    """Scale to fill `size`; y_bias 0 keeps the top, 1 keeps the bottom."""
    w, h = size
    scale = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * scale), math.ceil(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - w) // 2, int((img.height - h) * y_bias)
    return img.crop((left, top, left + w, top + h))


# ---------------------------------------------------------------- composite

def _grade_background(bg: Image.Image, bottom: int) -> Image.Image:
    """Make any generated scene read as a soft-focus studio set around a sharp product.

    Brightens dark scenes towards the product photo's studio exposure, calms saturation so
    the label stays the most colourful thing in frame, and applies depth of field that is
    strongest at the back wall and nearly sharp at the tabletop where the jar stands.
    """
    arr = np.asarray(bg.convert("RGB")).astype(np.float32) / 255.0
    lum = float((arr[..., 0] * 0.299 + arr[..., 1] * 0.587 + arr[..., 2] * 0.114).mean())
    if lum < 0.62:
        arr = arr ** (math.log(0.62) / math.log(max(lum, 0.05)))
    grey = arr.mean(axis=2, keepdims=True)
    arr = grey + (arr - grey) * 0.86
    arr = arr * np.array([1.02, 1.0, 0.96], np.float32)
    return _depth_of_field(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)), bottom)


def _depth_of_field(img: Image.Image, bottom: int) -> Image.Image:
    """Blur strongest at the back wall, nearly sharp at the tabletop where the jar stands."""
    img = img.convert("RGB")
    far = img.filter(ImageFilter.GaussianBlur(7))
    mid = img.filter(ImageFilter.GaussianBlur(3))
    near = img.filter(ImageFilter.GaussianBlur(1.2))
    y = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    focus = bottom / H
    to_mid = np.clip((y - 0.35) / max(focus - 0.35, 1e-3), 0, 1)
    out = np.asarray(far, np.float32)
    out = out + (np.asarray(mid, np.float32) - out) * np.clip(to_mid * 2, 0, 1)[..., None]
    out = out + (np.asarray(near, np.float32) - out) * np.clip(to_mid * 2 - 1, 0, 1)[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")


def _backlight(canvas: Image.Image, cx: int, cy: int, rx: int, ry: int) -> None:
    """Soft warm halo behind the product, like a studio background light."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    glow = np.exp(-d * 1.6)[..., None] * 0.30
    arr = np.asarray(canvas.convert("RGB"), np.float32)
    arr = arr + (np.array([255, 250, 238], np.float32) - arr) * glow
    canvas.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"))


def _vignette(canvas: Image.Image, strength: float = 0.22) -> None:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.55) / (H / 2)) ** 2)
    shade = 1.0 - np.clip(d - 0.6, 0, 1) * strength
    arr = np.asarray(canvas.convert("RGB"), np.float32) * shade[..., None]
    canvas.paste(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"))


def _shadow_layer(size: tuple[int, int], shapes: list[tuple], blur: float) -> Image.Image:
    layer = Image.new("L", size, 0)
    d = ImageDraw.Draw(layer)
    for box, value in shapes:
        d.ellipse(box, fill=value)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def _place(canvas: Image.Image, cut: Image.Image, height: int, cx: int, bottom: int, light_left: bool = True) -> None:
    """Seat the jar on the tabletop: ambient occlusion, a soft cast shadow falling away
    from the key light, a faint table reflection, then the untouched jar."""
    scale = height / cut.height
    jar = cut.resize((max(1, round(cut.width * scale)), height), Image.LANCZOS)
    x, y = cx - jar.width // 2, bottom - jar.height
    jw = jar.width

    # Faint reflection: the jar's lower part mirrored into the tabletop, fading quickly.
    refl_h = int(height * 0.14)
    mirror = jar.transpose(Image.FLIP_TOP_BOTTOM).crop((0, 0, jw, refl_h))
    fade = np.linspace(0.13, 0.0, refl_h, dtype=np.float32)[:, None]
    ra = (np.asarray(mirror.getchannel("A"), np.float32) * fade).astype(np.uint8)
    mirror.putalpha(Image.fromarray(ra))
    canvas.alpha_composite(mirror.filter(ImageFilter.GaussianBlur(2.5)), (x, bottom))

    darkness = Image.new("RGBA", canvas.size, (28, 18, 10, 255))
    near, far = (0.35, 1.05) if light_left else (1.05, 0.35)

    # Cast shadow: long soft ellipse pushed away from the light, back along the table plane.
    cast = _shadow_layer(canvas.size, [
        ((cx - jw * near, bottom - jw * 0.16, cx + jw * far, bottom + jw * 0.02), 95),
    ], blur=jw * 0.09)
    # Ground shadow directly under the jar, then a tight dark occlusion line at the base.
    gl, gr = (0.58, 0.62) if light_left else (0.62, 0.58)
    ground = _shadow_layer(canvas.size, [
        ((cx - jw * gl, bottom - jw * 0.07, cx + jw * gr, bottom + jw * 0.05), 120),
    ], blur=jw * 0.05)
    contact = _shadow_layer(canvas.size, [
        ((cx - jw * 0.47, bottom - jw * 0.025, cx + jw * 0.49, bottom + jw * 0.02), 215),
    ], blur=max(2.0, jw * 0.012))

    for mask in (cast, ground, contact):
        layer = darkness.copy()
        layer.putalpha(mask)
        canvas.alpha_composite(layer)

    canvas.alpha_composite(jar, (x, y))


def compose(
    background: Image.Image,
    handles: list[str],
    y_bias: float = 0.5,
    base: float = 0.92,
    grade: bool = True,
    light_left: bool = True,
) -> Image.Image:
    """`base` is where the jar stands (fraction of height); `grade` evens out exposure and
    saturation for unvetted AI scenes — curated library scenes skip it to keep their mood."""
    cuts = [product_cutout(h) for h in handles[:3]]
    main_bottom = int(H * base)
    main_h = min(int(H * (0.70 if len(cuts) == 1 else 0.66)), int(main_bottom - H * 0.06))

    canvas = _cover(background, (W, H), y_bias)
    canvas = _grade_background(canvas, main_bottom) if grade else _depth_of_field(canvas, main_bottom)
    _backlight(canvas, W // 2, int(main_bottom - main_h * 0.55), int(W * 0.30), int(H * 0.45))
    _vignette(canvas)

    if len(cuts) > 1:
        side_h = int(main_h * 0.80)
        main_w = cuts[0].width * main_h / cuts[0].height
        side_bottom = main_bottom - int(H * 0.035)
        for i, cut in enumerate(cuts[1:]):
            side_w = cut.width * side_h / cut.height
            offset = int(main_w / 2 + side_w * 0.30)
            _place(canvas, cut, side_h, W // 2 - offset if i == 0 else W // 2 + offset, side_bottom, light_left)

    _place(canvas, cuts[0], main_h, W // 2, main_bottom, light_left)
    return canvas.convert("RGB")


def topic_handles(topic: dict) -> list[str]:
    handles = [h for h in (topic.get("product_handles") or []) if h in PRODUCTS]
    return handles or [next(iter(PRODUCTS))]


def _chain(provider: str) -> list[str]:
    if provider in ("library", "cloudflare", "openai"):
        return [provider]
    if provider != "auto":
        return []
    chain = ["library"]
    if os.environ.get("CLOUDFLARE_ACCOUNT_ID") and os.environ.get("CLOUDFLARE_API_TOKEN"):
        chain.append("cloudflare")
    if os.environ.get("OPENAI_API_KEY"):
        chain.append("openai")
    return chain


def render(topic: dict, provider: str | None = None) -> tuple[Image.Image, str]:
    provider = (provider or os.environ.get("BLOG_IMAGE_PROVIDER", "auto")).strip().lower()
    handles = topic_handles(topic)
    for name in _chain(provider):
        try:
            if name == "library":
                bg, base, light_left = library_background(topic)
                return compose(bg, handles, base=base, grade=False, light_left=light_left), name
            if name == "cloudflare":
                seed = _seed(topic.get("id", ""), topic.get("title", "")) & 0x7FFFFFFF
                bg = cloudflare_background(build_flux_prompt(topic, handles), seed)
                # The schnell fallback is square; keep its lower part so the tabletop sits under the jars.
                return compose(bg, handles, y_bias=0.75), name
            return compose(openai_background(build_prompt(topic, handles)), handles), name
        except Exception as e:  # noqa: BLE001 — never block a publish on image generation
            print(f"   image: {name} background failed ({e}); trying next option")
    return compose(local_background(topic), handles), "local"


def featured_image_payload(topic: dict, title: str) -> dict | None:
    """Shopify article `image` payload with a freshly generated JPEG, or None to keep the raw photo."""
    if os.environ.get("BLOG_IMAGE_PROVIDER", "auto").strip().lower() == "off":
        return None
    try:
        img, used = render(topic)
    except Exception as e:  # noqa: BLE001
        print(f"   image: generation failed ({e}); falling back to product photo")
        return None
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88, optimize=True, progressive=True)
    out_dir = os.environ.get("BLOG_IMAGE_OUT_DIR")
    if out_dir:
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        (Path(out_dir) / f"{_slug(title)[:70]}.jpg").write_bytes(buf.getvalue())
    print(f"   image: generated {img.width}x{img.height} via {used} ({len(buf.getvalue()) // 1024} KB)")
    return {
        "attachment": base64.b64encode(buf.getvalue()).decode(),
        "alt": f"{title} — The Pickle Affair",
    }


def _find_topic(topic_id: str) -> dict:
    lib = json.loads((ROOT / "scratch" / "topic_library.json").read_text())
    for t in lib.get("topics", []) + lib.get("pillars", []):
        if t.get("id") == topic_id:
            return t
    raise SystemExit(f"Unknown topic id: {topic_id}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Preview a Kitchen Tales featured image")
    ap.add_argument("topic_id")
    ap.add_argument("--out", default="")
    ap.add_argument("--provider", default=None, choices=["auto", "library", "cloudflare", "openai", "local"])
    args = ap.parse_args()
    topic = _find_topic(args.topic_id)
    img, used = render(topic, args.provider)
    out = Path(args.out or f"{args.topic_id}.jpg")
    img.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"Saved {out} ({used})")


if __name__ == "__main__":
    sys.exit(main())
