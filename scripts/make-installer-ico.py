"""Build a BMP-based .ico for NSIS (PNG-in-ICO often fails as exe icon)."""
from __future__ import annotations

import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src-tauri" / "icons" / "icon.png"
OUT = ROOT / "src-tauri" / "icons" / "installer.ico"
SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


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


def main() -> None:
    img = Image.open(SRC).convert("RGBA")
    imgs = [img.resize(s, Image.Resampling.LANCZOS) for s in SIZES]
    entries: list[tuple[int, int, int, int]] = []
    images_data: list[bytes] = []
    offset = 6 + 16 * len(SIZES)
    for im in imgs:
        data = rgba_to_bmp_dib(im)
        w, h = im.size
        entries.append((0 if w >= 256 else w, 0 if h >= 256 else h, len(data), offset))
        images_data.append(data)
        offset += len(data)

    buf = bytearray()
    buf += struct.pack("<HHH", 0, 1, len(SIZES))
    for w, h, size, off in entries:
        buf += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, size, off)
    for data in images_data:
        buf += data

    OUT.write_bytes(buf)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    b = OUT.read_bytes()
    n = struct.unpack_from("<H", b, 4)[0]
    for i in range(n):
        o = 6 + i * 16
        w, h = b[o], b[o + 1]
        size, off = struct.unpack_from("<II", b, o + 8)
        print(f"  {i}: {w}x{h} size={size} dib_hdr={b[off]:02X}{b[off+1]:02X}")


if __name__ == "__main__":
    main()
