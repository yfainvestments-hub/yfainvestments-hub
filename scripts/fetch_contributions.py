"""Fetch the contribution calendar that GitHub uses to draw the profile graph.

Primary source is the GraphQL API, which is authoritative and exact. The catch
is *whose* token asks: contributions in private repos are only returned to a
viewer that can see those repos. This account is ~96% private, so:

  * GH_CONTRIB_TOKEN (a personal token with read:user) -> full picture.
  * The Actions-provided GITHUB_TOKEN -> github-actions[bot], which cannot see
    this user's private repos and silently reports only the public handful.
    It is deliberately NOT used here; doing so is what made the heatmap render
    ~41 contributions instead of ~1,148.

Without a personal token we fall back to scraping the public profile page,
which reports private counts while "Include private contributions on my
profile" is enabled in GitHub settings.
"""
from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = "yfainvestments-hub"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"
API = "https://api.github.com/graphql"
PROFILE_URL = f"https://github.com/users/{USERNAME}/contributions"

# Only an explicit personal token. See the module docstring for why the ambient
# Actions GITHUB_TOKEN must not be substituted here.
TOKEN = os.environ.get("GH_CONTRIB_TOKEN", "")

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


def fetch_graphql() -> list[dict] | None:
    """Authoritative. Returns None when no personal token is configured."""
    if not TOKEN:
        return None
    response = requests.post(
        API,
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": f"{USERNAME}-profile/1.0",
        },
        timeout=30,
    )
    if response.status_code != 200:
        print(f"GraphQL HTTP {response.status_code}; falling back to the profile page")
        return None
    body = response.json()
    if body.get("errors"):
        print(f"GraphQL errors: {body['errors']}; falling back to the profile page")
        return None

    calendar = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [
        {
            "date": day["date"],
            "count": day["contributionCount"],
            "level": LEVELS.get(day["contributionLevel"], 0),
        }
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    print(f"Fetched {len(days)} days via GraphQL ({calendar['totalContributions']} contributions)")
    return days


def contribution_count(soup: BeautifulSoup, cell) -> int:
    tooltip = soup.find("tool-tip", attrs={"for": cell.get("id")})
    if tooltip is None:
        return 0
    match = re.search(r"(\d[\d,]*) contributions?", tooltip.get_text(" ", strip=True))
    return int(match.group(1).replace(",", "")) if match else 0


def fetch_scrape() -> list[dict]:
    response = requests.get(
        PROFILE_URL,
        headers={"Accept": "text/html", "User-Agent": f"{USERNAME}-profile/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    days = [
        {
            "date": cell["data-date"],
            "count": contribution_count(soup, cell),
            "level": int(cell.get("data-level", 0)),
        }
        for cell in soup.select("td.ContributionCalendar-day[data-date]")
    ]
    print(f"Fetched {len(days)} days by scraping the profile page")
    return days


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


def guard_against_regression(total: int, active: int) -> None:
    """A sudden collapse means the querying identity lost sight of the private
    repos, not that a year of work vanished. Fail loudly rather than publish it."""
    if os.environ.get("ALLOW_CONTRIB_DROP") == "1" or not OUTPUT.exists():
        return
    try:
        prior_total = json.loads(OUTPUT.read_text(encoding="utf-8"))["stats"].get("total", 0)
    except (json.JSONDecodeError, KeyError, OSError):
        # Corrupt or half-merged file: nothing trustworthy to compare against.
        print("Previous contributions.json unreadable; skipping regression guard")
        return
    if prior_total >= 50 and total < prior_total * 0.5:
        raise RuntimeError(
            f"Refusing to overwrite: total fell from {prior_total:,} to {total:,} "
            f"({active} active days). Private contributions are probably invisible "
            "to the querying token - set GH_CONTRIB_TOKEN, or check the "
            "'Include private contributions on my profile' setting. "
            "Set ALLOW_CONTRIB_DROP=1 to override."
        )


def main() -> None:
    days = fetch_graphql() or fetch_scrape()
    days.sort(key=lambda item: item["date"])
    if len(days) < 350:
        raise RuntimeError(f"Expected a full contribution year, received {len(days)} days")

    total = sum(day["count"] for day in days)
    active_days = sum(day["count"] > 0 for day in days)
    guard_against_regression(total, active_days)

    current, longest = streaks(days)
    monthly = defaultdict(int)
    for day in days:
        monthly[day["date"][:7]] += day["count"]
    best = max(days, key=lambda item: item["count"])

    payload = {
        "username": USERNAME,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": API if TOKEN else PROFILE_URL,
        "days": days,
        "stats": {
            "total": total,
            "active_days": active_days,
            "current_streak": current,
            "longest_streak": longest,
            "best_day": best,
            "monthly_totals": dict(sorted(monthly.items())),
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days, {total} contributions to {OUTPUT}")


if __name__ == "__main__":
    main()
