"""Fetch the contribution calendar straight from GitHub's GraphQL API.

This is the authoritative source GitHub uses to draw the profile graph, so the
counts match exactly (and include private contributions when the querying token
has access). It is far more robust than scraping the public HTML calendar.

Requires a token in GITHUB_TOKEN (the nightly workflow passes the built-in
Actions token; locally, export GITHUB_TOKEN=$(gh auth token))."""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests


USERNAME = "yfainvestments-hub"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"
API = "https://api.github.com/graphql"
LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}
QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = running = 0
    by_date = {date.fromisoformat(day["date"]): day["count"] for day in days}
    for day in sorted(by_date):
        running = running + 1 if by_date[day] > 0 else 0
        longest = max(longest, running)

    cursor = max(by_date)
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required (export GITHUB_TOKEN=$(gh auth token))")

    response = requests.post(
        API,
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": f"{USERNAME}-profile/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    body = response.json()
    if body.get("errors"):
        raise SystemExit(f"GraphQL errors: {body['errors']}")

    calendar = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append(
                {
                    "date": day["date"],
                    "count": day["contributionCount"],
                    "level": LEVELS.get(day["contributionLevel"], 0),
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
        "source": "GitHub GraphQL contributionsCollection",
        "days": days,
        "stats": {
            "total": calendar["totalContributions"],
            "active_days": sum(day["count"] > 0 for day in days),
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best,
            "monthly_totals": dict(sorted(monthly.items())),
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days, {payload['stats']['total']} contributions to {OUTPUT}")


if __name__ == "__main__":
    main()
