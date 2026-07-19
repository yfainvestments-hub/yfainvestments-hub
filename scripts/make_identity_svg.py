from __future__ import annotations

import os
from html import escape
from pathlib import Path

import requests
from PIL import Image, ImageEnhance, ImageOps


USERNAME = "yfainvestments-hub"
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "avatar.png"
OUTPUT = ROOT / "identity-ascii.svg"
RAMP = "@%#*+=-:. "
COLS, ROWS = 50, 34
WIDTH, HEIGHT = 350, 300


def refresh_avatar() -> None:
    """Pull the account's current GitHub avatar so the ASCII art tracks the live
    profile picture. Falls back to the committed assets/avatar.png on any failure
    (offline, rate limit, API change) so the build never breaks."""
    headers = {"User-Agent": f"{USERNAME}-profile/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        api = requests.get(
            f"https://api.github.com/users/{USERNAME}",
            headers={**headers, "Accept": "application/vnd.github+json"},
            timeout=30,
        )
        api.raise_for_status()
        avatar_url = api.json()["avatar_url"]
        sep = "&" if "?" in avatar_url else "?"
        image = requests.get(f"{avatar_url}{sep}s=512", headers=headers, timeout=30)
        image.raise_for_status()
        SOURCE.parent.mkdir(parents=True, exist_ok=True)
        SOURCE.write_bytes(image.content)
        print(f"Refreshed avatar from {avatar_url}")
    except Exception as exc:  # noqa: BLE001 - deliberately fall back to committed image
        print(f"Could not refresh avatar ({exc}); using existing {SOURCE}")


def main() -> None:
    refresh_avatar()
    image = Image.open(SOURCE).convert("RGB")
    image = ImageOps.fit(image, (COLS, ROWS), method=Image.Resampling.LANCZOS)
    gray = ImageEnhance.Contrast(ImageOps.grayscale(image)).enhance(1.7)
    lines = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            value = gray.getpixel((x, y))
            chars.append(RAMP[min(len(RAMP) - 1, value * len(RAMP) // 256)])
        lines.append("".join(chars).rstrip())

    clips, rows = [], []
    start_y, line_height = 48, 6.35
    for index, line in enumerate(lines):
        y = start_y + index * line_height
        begin = 0.2 + index * 0.035
        clips.append(
            f'<clipPath id="line-{index}"><rect x="18" y="{y - 6:.2f}" height="8" width="0">'
            f'<animate attributeName="width" from="0" to="314" dur="0.42s" begin="{begin:.3f}s" fill="freeze" />'
            f'</rect></clipPath>'
        )
        rows.append(
            f'<text x="18" y="{y:.2f}" clip-path="url(#line-{index})">{escape(line)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">YFA identity mark rendered as animated ASCII art</title>
<desc id="desc">The YFA logo types itself row by row inside a terminal panel.</desc>
<defs>{''.join(clips)}</defs>
<style>text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 7px; font-weight: 700; fill: #bd83d6; white-space: pre; }}</style>
<rect width="348" height="298" x="1" y="1" rx="16" fill="#100b16" stroke="#3d2a49" />
<circle cx="20" cy="20" r="4.5" fill="#ff6b81"/><circle cx="36" cy="20" r="4.5" fill="#f6c85f"/><circle cx="52" cy="20" r="4.5" fill="#65d6a6"/>
<text x="67" y="24" style="font-size:10px;fill:#a993b8">identity.svg</text>
{''.join(rows)}
<rect x="18" y="275" width="8" height="12" fill="#bd83d6"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite" /></rect>
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

