"""Render the background-removed avatar (assets/avatar-cutout.png, produced by
scripts/prep_avatar.py) as an animated ASCII portrait with a transparent
background and no terminal panel, so it floats on the GitHub page.

This reads a committed, pre-isolated source image and does no network I/O, so it
is safe to run in the nightly workflow. To refresh the source after changing the
GitHub profile picture, run scripts/prep_avatar.py first (needs rembg)."""
from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "avatar-cutout.png"
OUTPUT = ROOT / "identity-ascii.svg"
# 70-level density ramp (dense -> sparse). The removed background is composited to
# white, which lands on the trailing space, so the backdrop renders as nothing.
RAMP = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
COLS = 110                # horizontal resolution (detail)
WIDTH, HEIGHT = 350, 300  # viewBox; 350 + info-card 510 = heatmap 860 (aligned)
CHAR_RATIO = 0.6          # monospace glyph advance width / font-size
LINE_RATIO = 0.92         # line height / font-size
PAD = 8                   # padding inside the viewBox
FILL = "#8e3fd6"          # deep enough to read on both GitHub light and dark themes


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    width, height = image.size
    # Derive ROWS from the source aspect so the portrait is not vertically
    # stretched once the tall-ish character cells are accounted for.
    rows = max(1, round(COLS * (height / width) * (CHAR_RATIO / LINE_RATIO)))

    small = image.resize((COLS, rows), Image.Resampling.LANCZOS)
    # Normalize the tonal range and lift shadows (gamma < 1) so a dark suit shows
    # texture across the ramp instead of crushing to a solid block of dense chars.
    gray = ImageOps.autocontrast(ImageOps.grayscale(small), cutoff=1)
    gray = gray.point(lambda value: int(255 * (value / 255) ** 0.55))
    lines = []
    for y in range(rows):
        line = "".join(
            RAMP[min(len(RAMP) - 1, gray.getpixel((x, y)) * len(RAMP) // 256)]
            for x in range(COLS)
        )
        lines.append(line.rstrip())

    box_w = WIDTH - 2 * PAD
    box_h = HEIGHT - 2 * PAD
    font_size = min(box_w / (COLS * CHAR_RATIO), box_h / (rows * LINE_RATIO))
    line_height = font_size * LINE_RATIO
    grid_w = COLS * CHAR_RATIO * font_size
    grid_h = rows * line_height
    start_x = (WIDTH - grid_w) / 2
    start_y = (HEIGHT - grid_h) / 2 + font_size

    clips, text_rows = [], []
    for index, line in enumerate(lines):
        y = start_y + index * line_height
        begin = 0.2 + index * 0.02
        clips.append(
            f'<clipPath id="line-{index}">'
            f'<rect x="{start_x:.2f}" y="{y - font_size:.2f}" height="{font_size + 2:.2f}" width="0">'
            f'<animate attributeName="width" from="0" to="{grid_w:.2f}" dur="0.45s" begin="{begin:.3f}s" fill="freeze" />'
            f'</rect></clipPath>'
        )
        text_rows.append(
            f'<text x="{start_x:.2f}" y="{y:.2f}" clip-path="url(#line-{index})">{escape(line)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">yfainvestments-hub rendered as animated ASCII art</title>
<desc id="desc">A portrait types itself in row by row over a transparent background.</desc>
<defs>{''.join(clips)}</defs>
<style>text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: {font_size:.2f}px; font-weight: 700; fill: {FILL}; white-space: pre; }}</style>
{''.join(text_rows)}
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({COLS}x{rows} chars, font {font_size:.2f}px)")


if __name__ == "__main__":
    main()
