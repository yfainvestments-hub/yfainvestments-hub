from __future__ import annotations

from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"
ROWS = [
    ("identity", "YFA Investments"),
    ("role", "founder + operator"),
    ("focus", "AI systems + compliance automation"),
    ("stack", "Python · JavaScript · React"),
    ("building", "LearnFi · PilotComply"),
    ("clearance", "active Secret (US)"),
    ("signal", "practical tools > hype"),
]


def main() -> None:
    rendered = []
    for index, (key, value) in enumerate(ROWS):
        y = 102 + index * 25
        begin = 0.35 + index * 0.2
        rendered.append(
            f'<g class="line" transform="translate(34 {y})">'
            f'<animate attributeName="opacity" values="0;1" dur="0.35s" begin="{begin:.2f}s" fill="freeze" />'
            f'<text class="key">{escape(key):>9}</text>'
            f'<text class="sep" x="100">:</text>'
            f'<text class="value" x="118">{escape(value)}</text></g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="510" height="300" viewBox="0 0 510 300" role="img" aria-labelledby="title desc">
<title id="title">YFA Investments terminal profile card</title>
<desc id="desc">Profile summary covering role, focus, technology stack, current project, and learning.</desc>
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .host {{ fill:#f4eaff; font-size:16px; font-weight:700; }}
  .prompt {{ fill:#65d6a6; font-size:12px; }}
  .key {{ fill:#bd83d6; font-size:12px; font-weight:700; }}
  .sep {{ fill:#6c5878; font-size:12px; }}
  .value {{ fill:#e7dceb; font-size:12px; }}
  .line {{ opacity:1; }}
</style>
<rect width="508" height="298" x="1" y="1" rx="16" fill="#100b16" stroke="#3d2a49" />
<circle cx="22" cy="22" r="5" fill="#ff6b81"/><circle cx="39" cy="22" r="5" fill="#f6c85f"/><circle cx="56" cy="22" r="5" fill="#65d6a6"/>
<text class="host" x="34" y="62">yfa@github</text><text class="prompt" x="150" y="62">~ $ whoami --verbose</text>
<line x1="34" y1="76" x2="476" y2="76" stroke="#3d2a49" />
{''.join(rendered)}
<text x="34" y="282" class="prompt">status: always building_</text>
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
