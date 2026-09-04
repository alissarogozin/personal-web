#!/usr/bin/env python3
"""Normalize a folder of object cut-outs to a consistent size and canvas.

For each image: trim the transparent/white padding down to the object's real
bounding box, scale the object so its longest side is a fixed length, then
center it on a fixed-size canvas. Outputs PNG, same filenames, to a new folder.

Requires Pillow:  pip install Pillow

Examples
--------
# Preview one file (writes a side-by-side comparison, changes nothing else)
python3 scripts/normalize_images.py images --preview

# Process the whole folder
python3 scripts/normalize_images.py images -o images-normalized

# White canvas instead of transparent, 512 object on a 640 canvas
python3 scripts/normalize_images.py images --bg white --longest 512 --canvas 640
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

# Extensions we'll read. Everything is written back out as .png.
SUFFIXES = {".png", ".tif", ".tiff", ".jpg", ".jpeg", ".webp", ".bmp"}


def has_real_alpha(im: Image.Image, threshold: int) -> bool:
    """True if the image carries an alpha channel that's actually used."""
    if im.mode not in ("RGBA", "LA", "PA") and "transparency" not in im.info:
        return False
    alpha = im.convert("RGBA").getchannel("A")
    lo, _hi = alpha.getextrema()
    return lo <= threshold


def object_bbox(im: Image.Image, mode: str, alpha_threshold: int, tolerance: int):
    """Bounding box of the object, or None if the image is entirely background.

    mode="alpha" keys off transparency; mode="white" off near-white pixels.
    Picking one matters: an object with a white border on a transparent
    background (a polaroid, say) loses its border if you trim white from it.
    """
    rgba = im.convert("RGBA")

    if mode == "alpha":
        mask = rgba.getchannel("A").point(lambda v: 255 if v > alpha_threshold else 0)
    else:
        # Flatten onto white first so transparent areas count as background too.
        flat = Image.alpha_composite(Image.new("RGBA", rgba.size, (255, 255, 255, 255)), rgba)
        diff = ImageChops.difference(flat.convert("RGB"), Image.new("RGB", rgba.size, (255, 255, 255)))
        mask = diff.convert("L").point(lambda v: 255 if v > tolerance else 0)

    return mask.getbbox()


def normalize(im: Image.Image, canvas: int, longest: int, bg: str,
              trim: str, alpha_threshold: int, tolerance: int):
    """Return (normalized RGBA image, info dict) or (None, info) if blank."""
    rgba = im.convert("RGBA")
    mode = trim
    if trim == "auto":
        mode = "alpha" if has_real_alpha(im, alpha_threshold) else "white"

    box = object_bbox(rgba, mode, alpha_threshold, tolerance)
    info = {"trim_mode": mode, "src_size": rgba.size, "bbox": box}
    if box is None:
        return None, info

    cropped = rgba.crop(box)
    w, h = cropped.size
    scale = longest / max(w, h)
    new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
    resized = cropped.resize(new_size, Image.LANCZOS)

    fill = (0, 0, 0, 0) if bg == "transparent" else (255, 255, 255, 255)
    out = Image.new("RGBA", (canvas, canvas), fill)
    out.paste(resized, ((canvas - new_size[0]) // 2, (canvas - new_size[1]) // 2), resized)

    info.update({"cropped_size": (w, h), "out_object_size": new_size, "scale": scale})
    return out, info


def checkerboard(size, square: int = 16):
    """Light checkerboard so transparency is visible in the preview."""
    img = Image.new("RGB", size, (255, 255, 255))
    d = ImageDraw.Draw(img)
    for y in range(0, size[1], square):
        for x in range(0, size[0], square):
            if (x // square + y // square) % 2:
                d.rectangle([x, y, x + square - 1, y + square - 1], fill=(226, 226, 226))
    return img


def make_preview(src_img: Image.Image, out_img: Image.Image, path: Path,
                 info: dict, dest: Path, cell: int = 520, pad: int = 28):
    """Write a labelled before/after comparison to `dest`."""
    try:
        font = ImageFont.load_default(16)
        small = ImageFont.load_default(13)
    except TypeError:  # Pillow < 10.1 ignores the size argument
        font = small = ImageFont.load_default()

    header, footer = 34, 26
    canvas = Image.new("RGB", (cell * 2 + pad * 3, cell + header + footer + pad * 2), (250, 249, 246))
    draw = ImageDraw.Draw(canvas)

    panels = [
        ("BEFORE  " + path.name, src_img, f"{src_img.width}x{src_img.height}  •  object bbox {info['bbox']}"),
        ("AFTER  " + path.stem + ".png", out_img,
         f"{out_img.width}x{out_img.height}  •  object {info['out_object_size'][0]}x{info['out_object_size'][1]}"
         f"  •  scale {info['scale']:.2f}x"),
    ]

    for i, (title, img, caption) in enumerate(panels):
        x = pad + i * (cell + pad)
        y = pad + header
        tile = checkerboard((cell, cell))
        fitted = img.copy()
        fitted.thumbnail((cell, cell), Image.LANCZOS)
        tile.paste(fitted, ((cell - fitted.width) // 2, (cell - fitted.height) // 2),
                   fitted.convert("RGBA"))
        canvas.paste(tile, (x, y))
        draw.rectangle([x, y, x + cell - 1, y + cell - 1], outline=(205, 201, 189))
        draw.text((x, pad + 8), title, fill=(20, 18, 12), font=font)
        draw.text((x, y + cell + 7), caption, fill=(110, 105, 92), font=small)

    canvas.save(dest)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", type=Path, help="folder of images to process")
    p.add_argument("-o", "--out", type=Path,
                   help="output folder (default: <src>-normalized)")
    p.add_argument("--canvas", type=int, default=1000, help="output canvas, square (default: 1000)")
    p.add_argument("--longest", type=int, default=800,
                   help="object's longest side after scaling (default: 800)")
    p.add_argument("--bg", choices=("transparent", "white"), default="transparent",
                   help="canvas background (default: transparent)")
    p.add_argument("--trim", choices=("auto", "alpha", "white"), default="auto",
                   help="what counts as padding. auto = alpha if the image has "
                        "any, else white (default: auto)")
    p.add_argument("--alpha-threshold", type=int, default=24,
                   help="alpha at or below this is background (default: 24)")
    p.add_argument("--tolerance", type=int, default=12,
                   help="how far from pure white still counts as background (default: 12)")
    p.add_argument("--preview", nargs="?", const="__first__", metavar="FILENAME",
                   help="process a single file and write a before/after comparison "
                        "instead of the whole folder")
    p.add_argument("--overwrite", action="store_true",
                   help="overwrite existing files in the output folder")
    args = p.parse_args()

    if not args.src.is_dir():
        print(f"error: {args.src} is not a folder", file=sys.stderr)
        return 1
    if args.longest > args.canvas:
        print(f"error: --longest ({args.longest}) exceeds --canvas ({args.canvas}); "
              "the object would be clipped", file=sys.stderr)
        return 1

    files = sorted(f for f in args.src.iterdir()
                   if f.is_file() and f.suffix.lower() in SUFFIXES and not f.name.startswith("."))
    if not files:
        print(f"error: no images found in {args.src}", file=sys.stderr)
        return 1

    out_dir = args.out or args.src.parent / (args.src.name + "-normalized")

    # --- preview mode: one file, nothing else touched -----------------------
    if args.preview:
        if args.preview == "__first__":
            target = files[0]
        else:
            matches = [f for f in files if f.name == args.preview or f.stem == args.preview]
            if not matches:
                print(f"error: {args.preview} not found in {args.src}", file=sys.stderr)
                return 1
            target = matches[0]

        with Image.open(target) as im:
            im.load()
            out_img, info = normalize(im, args.canvas, args.longest, args.bg,
                                      args.trim, args.alpha_threshold, args.tolerance)
            if out_img is None:
                print(f"error: {target.name} looks entirely blank; nothing to trim",
                      file=sys.stderr)
                return 1
            dest = out_dir / "_preview.png"
            dest.parent.mkdir(parents=True, exist_ok=True)
            make_preview(im, out_img, target, info, dest)

        print(f"preview:      {dest}")
        print(f"source:       {target.name}  {info['src_size'][0]}x{info['src_size'][1]}")
        print(f"trim mode:    {info['trim_mode']}")
        print(f"object bbox:  {info['bbox']}  ->  {info['cropped_size'][0]}x{info['cropped_size'][1]}")
        print(f"scaled:       {info['out_object_size'][0]}x{info['out_object_size'][1]}"
              f"  ({info['scale']:.2f}x)")
        print(f"canvas:       {args.canvas}x{args.canvas}, {args.bg}")
        print(f"\n{len(files)} image(s) queued. Re-run without --preview to process them all.")
        return 0

    # --- full run -----------------------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    written = skipped = 0
    for f in files:
        dest = out_dir / (f.stem + ".png")
        if dest.exists() and not args.overwrite:
            print(f"skip   {f.name}  (exists: {dest.name}; use --overwrite)")
            skipped += 1
            continue
        try:
            with Image.open(f) as im:
                im.load()
                out_img, info = normalize(im, args.canvas, args.longest, args.bg,
                                          args.trim, args.alpha_threshold, args.tolerance)
        except Exception as exc:  # unreadable/corrupt file shouldn't kill the batch
            print(f"skip   {f.name}  ({exc})")
            skipped += 1
            continue

        if out_img is None:
            print(f"skip   {f.name}  (no object found — entirely background?)")
            skipped += 1
            continue

        out_img.save(dest)
        note = "  UPSCALED" if info["scale"] > 1.5 else ""
        print(f"ok     {f.name}  {info['src_size'][0]}x{info['src_size'][1]}"
              f" -> object {info['out_object_size'][0]}x{info['out_object_size'][1]}"
              f" on {args.canvas}x{args.canvas}  [{info['trim_mode']}]{note}")
        written += 1

    print(f"\n{written} written, {skipped} skipped -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
