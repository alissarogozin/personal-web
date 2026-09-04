#!/usr/bin/env python3
"""Derive the Photography grid's web assets from photo collage/.

photo collage/ is the source of truth: full-resolution travel photos, each
named after (or otherwise identifying) the location it was taken. This
script resizes them for a grid of thumbnails — not full-bleed images — and
writes WebP, which is a fraction of the JPEG weight at the same quality.

Requires Pillow:  pip install Pillow
Usage:            python3 scripts/build_photography_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

SRC = Path("photo collage")
DEST = Path("public/assets/photography")
MAX_EDGE = 1200
QUALITY = 82

# source filename -> (slug used in the grid, display label for the caption).
# The two "location" filenames had typos (Amsterdamn, Herzogevina) fixed in
# the label only. IMG_2142.jpeg carries no location in its name; matched by
# its Nyhavn (Copenhagen) architecture — flagged in the script output below
# so it can be corrected if that's wrong.
MAPPING = {
    "Amsterdamn, Netherlands.jpeg": ("amsterdam", "Amsterdam, Netherlands"),
    "Beijing, China.JPG": ("beijing", "Beijing, China"),
    "Dubrovnik, Croatia.jpeg": ("dubrovnik", "Dubrovnik, Croatia"),
    "IMG_2142.jpeg": ("copenhagen", "Copenhagen, Denmark"),
    "Mostar, Bosnia and Herzogevina.jpeg": ("mostar", "Mostar, Bosnia and Herzegovina"),
    "Prague, Czech Republic.jpeg": ("prague", "Prague, Czech Republic"),
    "San Francisco, California.jpeg": ("san-francisco", "San Francisco, California"),
    "Sedona, Arizona.jpeg": ("sedona", "Sedona, Arizona"),
    "Split, Croatia.jpeg": ("split", "Split, Croatia"),
    "Strasbourg, France.jpeg": ("strasbourg", "Strasbourg, France"),
}


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, (slug, label) in MAPPING.items():
        src = SRC / name
        if not src.exists():
            print(f"MISSING  {src}")
            continue
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)  # respect phone-camera orientation
            im = im.convert("RGB")
            w, h = im.size
            scale = MAX_EDGE / max(w, h)
            if scale < 1:
                im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
            dest = DEST / f"{slug}.webp"
            im.save(dest, "WEBP", quality=QUALITY, method=6)
        flag = "  <- confirm this is really Copenhagen" if slug == "copenhagen" else ""
        print(f"{slug:<14} {label:<32} -> {dest.name} {dest.stat().st_size // 1024}KB{flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
