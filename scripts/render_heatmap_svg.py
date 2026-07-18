from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"
PALETTE = ["#21152d", "#42205f", "#6f3693", "#9858bb", "#bd83d6"]
WIDTH, HEIGHT = 860, 205
GRID_X, GRID_Y = 42, 62
STEP, CELL = 15, 11


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    days = payload["days"]
    stats = payload["stats"]
    first = date.fromisoformat(days[0]["date"])

    month_labels = []
    seen_months = set()
    cells = []
    for item in days:
        current = date.fromisoformat(item["date"])
        week = (current - first).days // 7
        weekday = (current.weekday() + 1) % 7
        x, y = GRID_X + week * STEP, GRID_Y + weekday * STEP
        month_key = current.strftime("%Y-%m")
        if month_key not in seen_months and weekday <= 2:
            seen_months.add(month_key)
            month_labels.append(
                f'<text class="month" x="{x}" y="48">{escape(current.strftime("%b"))}</text>'
            )
        level = max(0, min(int(item["level"]), len(PALETTE) - 1))
        delay = 0.18 + (week + weekday) * 0.018
        label = f'{item["count"]} contributions on {current.strftime("%B %d, %Y")}'
        cells.append(
            f'<rect class="day" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s">'
            f'<title>{escape(label)}</title></rect>'
        )

    legend_x = 705
    legend = [f'<text class="muted" x="{legend_x - 38}" y="185">Less</text>']
    for index, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + index * 17}" y="175" width="11" height="11" rx="3" fill="{color}" />'
        )
    legend.append(f'<text class="muted" x="{legend_x + 91}" y="185">More</text>')

    subtitle = (
        f'{stats["total"]:,} contributions · {stats["active_days"]} active days · '
        f'{stats["longest_streak"]}-day longest streak'
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">Contribution activity for {escape(payload["username"])}</title>
<desc id="desc">{escape(subtitle)}</desc>
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  .title {{ fill: #f4eaff; font-size: 16px; font-weight: 700; }}
  .muted, .month, .weekday {{ fill: #a993b8; font-size: 10px; }}
  .day {{ opacity: 0; transform: translateY(-8px); animation: reveal .36s cubic-bezier(.2,.8,.2,1) forwards; }}
  @keyframes reveal {{ to {{ opacity: 1; transform: translateY(0); }} }}
  @media (prefers-reduced-motion: reduce) {{ .day {{ opacity: 1; transform: none; animation: none; }} }}
</style>
<rect width="858" height="203" x="1" y="1" rx="16" fill="#100b16" stroke="#3d2a49" />
<circle cx="22" cy="22" r="5" fill="#ff6b81"/><circle cx="39" cy="22" r="5" fill="#f6c85f"/><circle cx="56" cy="22" r="5" fill="#65d6a6"/>
<text class="title" x="76" y="28">contribution activity</text>
{''.join(month_labels)}
<text class="weekday" x="15" y="89">Mon</text><text class="weekday" x="15" y="119">Wed</text><text class="weekday" x="15" y="149">Fri</text>
{''.join(cells)}
<text class="muted" x="42" y="185">{escape(subtitle)}</text>
{''.join(legend)}
</svg>
'''
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()

