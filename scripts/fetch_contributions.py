from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "yfainvestments-hub"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"


def contribution_count(soup: BeautifulSoup, cell) -> int:
    tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
    if tooltip is None:
        return 0
    match = re.search(r"(\d[\d,]*) contributions?", tooltip.get_text(" ", strip=True))
    return int(match.group(1).replace(",", "")) if match else 0


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = running = 0
    by_date = {date.fromisoformat(day["date"]): day["count"] for day in days}
    for day in sorted(by_date):
        running = running + 1 if by_date[day] > 0 else 0
        longest = max(longest, running)

    cursor = date.today()
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def main() -> None:
    response = requests.get(
        URL,
        headers={
            "Accept": "text/html",
            "User-Agent": "yfainvestments-hub-profile/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append(
            {
                "date": cell["data-date"],
                "count": contribution_count(soup, cell),
                "level": int(cell.get("data-level", 0)),
            }
        )
    days.sort(key=lambda item: item["date"])
    if len(days) < 350:
        raise RuntimeError(f"Expected a full contribution year, received {len(days)} days")

    current, longest = streaks(days)
    monthly = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]
    best = max(days, key=lambda item: item["count"])

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": URL,
        "days": days,
        "stats": {
            "total": sum(day["count"] for day in days),
            "active_days": sum(day["count"] > 0 for day in days),
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best,
            "monthly_totals": dict(sorted(monthly.items())),
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days and {payload['stats']['total']} contributions to {OUTPUT}")


if __name__ == "__main__":
    main()

