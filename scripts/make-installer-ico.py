"""Build crisp Windows shell icons (BMP ICO) from branding/tomo-icon.png.

Small sizes (16–48) are redrawn with thicker strokes so the reticle stays
readable on the desktop — LANCZOS of the full art collapses into a plain T.
"""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "branding" / "tomo-icon.png"
ICON_PNG = ROOT / "src-tauri" / "icons" / "icon.png"
OUTS = [
    ROOT / "src-tauri" / "icons" / "installer.ico",
    ROOT / "src-tauri" / "icons" / "icon.ico",
]
PNG_SIZES = {
    32: ROOT / "src-tauri" / "icons" / "32x32.png",
    64: ROOT / "src-tauri" / "icons" / "64x64.png",
    128: ROOT / "src-tauri" / "icons" / "128x128.png",
    256: ROOT / "src-tauri" / "icons" / "128x128@2x.png",
}
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]


def draw_reticle(size: int) -> Image.Image:
    """Vector-ish reticle that stays legible at tiny desktop sizes."""
    bg = (12, 4, 4, 255)
    im = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(im)
    cx = cy = (size - 1) / 2.0

    # Scale stroke widths for readability
    if size <= 16:
        outer_w, inner_w, bar_w, stem_w, tick_w, sq = 1.5, 1.0, 2.0, 1.5, 1.0, 2
        r_outer, r_inner = size * 0.40, size * 0.28
        bar_y, bar_half = size * 0.34, size * 0.22
        stem_top, stem_bot = size * 0.34, size * 0.78
    elif size <= 32:
        outer_w, inner_w, bar_w, stem_w, tick_w, sq = 2.0, 1.5, 3.0, 2.0, 1.5, 3
        r_outer, r_inner = size * 0.40, size * 0.28
        bar_y, bar_half = size * 0.34, size * 0.24
        stem_top, stem_bot = size * 0.34, size * 0.78
    elif size <= 48:
        outer_w, inner_w, bar_w, stem_w, tick_w, sq = 2.2, 1.6, 3.5, 2.2, 1.6, 4
        r_outer, r_inner = size * 0.40, size * 0.28
        bar_y, bar_half = size * 0.33, size * 0.25
        stem_top, stem_bot = size * 0.33, size * 0.78
    else:
        # For larger sizes prefer the master art when available
        return None  # type: ignore

    white = (232, 200, 200, 255)
    red = (255, 59, 48, 255)
    red_dim = (106, 48, 48, 255)

    # Outer + inner rings
    bbox = [cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer]
    d.ellipse(bbox, outline=white, width=max(1, int(round(outer_w))))
    bbox_i = [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner]
    d.ellipse(bbox_i, outline=red_dim, width=max(1, int(round(inner_w))))

    # Cardinal ticks (red)
    tick = max(2, int(size * 0.07))
    tw = max(1, int(round(tick_w)))
    d.line([(cx, cy - r_outer - 1), (cx, cy - r_outer + tick)], fill=red_dim, width=tw)
    d.line([(cx, cy + r_outer - tick), (cx, cy + r_outer + 1)], fill=red_dim, width=tw)
    d.line([(cx - r_outer - 1, cy), (cx - r_outer + tick, cy)], fill=red_dim, width=tw)
    d.line([(cx + r_outer - tick, cy), (cx + r_outer + 1, cy)], fill=red_dim, width=tw)

    # White T-bar
    bw = max(1, int(round(bar_w)))
    d.line([(cx - bar_half, bar_y), (cx + bar_half, bar_y)], fill=white, width=bw)

    # Red stem
    sw = max(1, int(round(stem_w)))
    d.line([(cx, stem_top), (cx, stem_bot)], fill=red, width=sw)

    # Center square
    hs = sq / 2.0
    d.rectangle([cx - hs, cy - hs, cx + hs, cy + hs], outline=red, width=max(1, sw - 1))
    # hollow core
    if sq >= 3:
        d.rectangle([cx - hs + 1, cy - hs + 1, cx + hs - 1, cy + hs - 1], fill=bg)

    return im


def master_resize(size: int) -> Image.Image:
    src = Image.open(MASTER).convert("RGBA")
    # Pad to square if needed
    side = max(src.size)
    canvas = Image.new("RGBA", (side, side), src.getpixel((2, 2)))
    canvas.paste(src, ((side - src.width) // 2, (side - src.height) // 2), src)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def make_size(size: int) -> Image.Image:
    drawn = draw_reticle(size)
    if drawn is not None:
        return drawn
    return master_resize(size)


def rgba_to_bmp_dib(im: Image.Image) -> bytes:
    w, h = im.size
    pixels = list(im.getdata())
    xor = bytearray()
    and_rows: list[bytes] = []
    for y in range(h - 1, -1, -1):
        row = pixels[y * w : (y + 1) * w]
        for r, g, b, a in row:
            xor += bytes((b, g, r, a))
        bits = 0
        bitc = 0
        mask_bytes = bytearray()
        for _r, _g, _b, a in row:
            bits = (bits << 1) | (1 if a < 128 else 0)
            bitc += 1
            if bitc == 8:
                mask_bytes.append(bits)
                bits = 0
                bitc = 0
        if bitc:
            mask_bytes.append(bits << (8 - bitc))
        while len(mask_bytes) % 4:
            mask_bytes.append(0)
        and_rows.append(bytes(mask_bytes))
    and_mask = b"".join(and_rows)
    header = struct.pack(
        "<IIIHHIIIIII",
        40,
        w,
        h * 2,
        1,
        32,
        0,
        len(xor),
        0,
        0,
        0,
        0,
    )
    return header + xor + and_mask


def write_ico(path: Path, imgs: list[Image.Image]) -> None:
    entries: list[tuple[int, int, int, int]] = []
    images_data: list[bytes] = []
    offset = 6 + 16 * len(imgs)
    for im in imgs:
        data = rgba_to_bmp_dib(im)
        w, h = im.size
        entries.append((0 if w >= 256 else w, 0 if h >= 256 else h, len(data), offset))
        images_data.append(data)
        offset += len(data)

    buf = bytearray()
    buf += struct.pack("<HHH", 0, 1, len(imgs))
    for w, h, size, off in entries:
        buf += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, size, off)
    for data in images_data:
        buf += data
    path.write_bytes(buf)
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"missing {MASTER}")

    # Master PNG for tauri / docs
    big = master_resize(512)
    ICON_PNG.parent.mkdir(parents=True, exist_ok=True)
    big.save(ICON_PNG)
    print(f"wrote {ICON_PNG}")

    for s, dest in PNG_SIZES.items():
        make_size(s).save(dest)
        print(f"wrote {dest}")

    imgs = [make_size(s) for s in ICO_SIZES]
    for out in OUTS:
        write_ico(out, imgs)

    # Preview the critical desktop size
    prev = ROOT / "branding" / "icon-32-preview.png"
    make_size(32).resize((128, 128), Image.Resampling.NEAREST).save(prev)
    print(f"wrote {prev}")


if __name__ == "__main__":
    main()
