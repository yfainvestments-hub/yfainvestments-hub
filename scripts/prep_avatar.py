"""Prepare the identity source image: fetch the live GitHub avatar, remove its
background with rembg, trim to the subject, and composite onto white so the
backdrop maps to the blank (space) end of the ASCII ramp.

This is a MANUAL prep step (rembg pulls a ~180MB model), not part of the nightly
workflow. Re-run it whenever the GitHub profile picture changes:

    python scripts/prep_avatar.py

It writes:
    assets/avatar.png          - raw avatar (reference)
    assets/avatar-cutout.png   - background-removed subject on white (ASCII source)
"""
from __future__ import annotations

import io
import os
from pathlib import Path

import requests
from PIL import Image
from rembg import remove


USERNAME = "yfainvestments-hub"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "assets" / "avatar.png"
CUTOUT = ROOT / "assets" / "avatar-cutout.png"
PAD = 0.06  # fraction of subject size added as breathing room around the crop


def fetch_avatar() -> Image.Image:
    headers = {"User-Agent": f"{USERNAME}-profile/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    api = requests.get(
        f"https://api.github.com/users/{USERNAME}",
        headers={**headers, "Accept": "application/vnd.github+json"},
        timeout=30,
    )
    api.raise_for_status()
    avatar_url = api.json()["avatar_url"]
    sep = "&" if "?" in avatar_url else "?"
    resp = requests.get(f"{avatar_url}{sep}s=512", headers=headers, timeout=30)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")


def main() -> None:
    raw = fetch_avatar()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    raw.convert("RGB").save(RAW)

    cut = remove(raw)  # RGBA with the background alpha-keyed out
    bbox = cut.getbbox()
    if bbox:
        left, upper, right, lower = bbox
        pad_x = int((right - left) * PAD)
        pad_y = int((lower - upper) * PAD)
        bbox = (
            max(0, left - pad_x),
            max(0, upper - pad_y),
            min(cut.width, right + pad_x),
            min(cut.height, lower + pad_y),
        )
        cut = cut.crop(bbox)

    white = Image.new("RGBA", cut.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white, cut).convert("RGB")
    composited.save(CUTOUT)
    print(f"Wrote {RAW} and {CUTOUT} ({composited.size[0]}x{composited.size[1]})")


if __name__ == "__main__":
    main()
