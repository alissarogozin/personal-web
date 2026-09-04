#!/usr/bin/env python3
"""Derive the hero's web assets from the standardized images in images/.

images/ is the source of truth: every object is centered on a 1000x1000
canvas with its longest side at 800px (see normalize_images.py). This script
maps those to the slugs CoverHero.astro expects and writes WebP, which is a
fraction of the PNG weight for photographic cut-outs with alpha.

It also prints each object's bounding box as a fraction of the canvas — the
CSS needs those numbers to place the bag, since the object no longer touches
the edges of its own file.

Requires Pillow:  pip install Pillow
Usage:            python3 scripts/build_hero_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

SRC = Path("images")
DEST = Path("public/assets/hero")
QUALITY = 88

# source filename -> slug used by CoverHero.astro
MAPPING = {
    "polaroid picture.png": "polaroid",
    "macbook icon.png": "macbook",
    "Passport icon.png": "passport",
    "walkie talkiepng.png": "walkie-talkie",
    "purse icon.png": "purse",
}


def content_box(im: Image.Image, alpha_threshold: int = 24):
    """Bounding box of the non-transparent object within the canvas."""
    alpha = im.convert("RGBA").getchannel("A")
    return alpha.point(lambda v: 255 if v > alpha_threshold else 0).getbbox()


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, slug in MAPPING.items():
        src = SRC / name
        if not src.exists():
            print(f"MISSING  {src}")
            continue
        with Image.open(src) as im:
            im = im.convert("RGBA")
            box = content_box(im)
            cw, ch = im.size
            dest = DEST / f"{slug}.webp"
            im.save(dest, "WEBP", quality=QUALITY, method=6)

        x0, y0, x1, y1 = box
        print(
            f"{slug:<14} {cw}x{ch} -> {dest.name} {dest.stat().st_size // 1024}KB   "
            f"object {x1 - x0}x{y1 - y0}  "
            f"w={ (x1 - x0) / cw :.3f} h={ (y1 - y0) / ch :.3f} "
            f"gap_below={ (ch - y1) / ch :.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
