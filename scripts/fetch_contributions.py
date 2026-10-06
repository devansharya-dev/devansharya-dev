from pathlib import Path
from datetime import datetime
import json
import os
import re
import requests
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
OUTPUT = ROOT / "data" / "contributions.json"

USERNAME = "devansharya-dev"

if not ENV_FILE.exists():
    raise RuntimeError(
        f".env file not found:\n{ENV_FILE}"
    )

env = dotenv_values(ENV_FILE)

TOKEN = None

for key, value in env.items():
    if not value:
        continue

    key_upper = key.upper()

    if (
        "GITHUB" in key_upper
        or "TOKEN" in key_upper
        or "PAT" in key_upper
    ):
        TOKEN = value.strip().strip('"').strip("'")
        break

if not TOKEN:
    raise RuntimeError(
        "No GitHub token found inside .env.\n"
        "Put your token in .env like:\n\n"
        "GITHUB_TOKEN=github_pat_xxxxxxxxx"
    )

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            color
            weekday
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print(f"Fetching contributions for @{USERNAME}...")

response = requests.post(
    "https://api.github.com/graphql",
    headers=headers,
    json={
        "query": QUERY,
        "variables": {
            "login": USERNAME
        }
    },
    timeout=30
)

response.raise_for_status()

result = response.json()

if "errors" in result:
    print(json.dumps(result["errors"], indent=2))
    raise RuntimeError(
        "GitHub GraphQL API returned an error."
    )

user = result.get("data", {}).get("user")

if not user:
    raise RuntimeError(
        f"GitHub user not found: {USERNAME}"
    )

calendar = (
    user["contributionsCollection"]
    ["contributionCalendar"]
)

level_map = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4
}

days = []

for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days.append({
            "date": day["date"],
            "count": day["contributionCount"],
            "level": level_map.get(
                day["contributionLevel"],
                0
            ),
            "color": day["color"],
            "weekday": day["weekday"]
        })

days.sort(key=lambda x: x["date"])

if not days:
    raise RuntimeError(
        "No contribution data received."
    )

total = calendar["totalContributions"]

best_day = max(
    days,
    key=lambda x: x["count"]
)

longest_streak = 0
streak = 0

for day in days:
    if day["count"] > 0:
        streak += 1
        longest_streak = max(
            longest_streak,
            streak
        )
    else:
        streak = 0

current_streak = 0

for day in reversed(days):
    if day["count"] > 0:
        current_streak += 1
    else:
        break

monthly_totals = {}

for day in days:
    month = day["date"][:7]

    monthly_totals[month] = (
        monthly_totals.get(month, 0)
        + day["count"]
    )

data = {
    "username": USERNAME,
    "updated_at": datetime.utcnow().isoformat() + "Z",
    "days": days,
    "stats": {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {
            "date": best_day["date"],
            "count": best_day["count"]
        }
    },
    "monthly_totals": monthly_totals
}

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT.write_text(
    json.dumps(
        data,
        indent=2
    ),
    encoding="utf-8"
)

print()
print("========================================")
print(" CONTRIBUTION DATA SAVED")
print("========================================")
print(f"File: {OUTPUT}")
print(f"Days: {len(days)}")
print(f"Total contributions: {total}")
print(f"Current streak: {current_streak}")
print(f"Longest streak: {longest_streak}")
print(
    f"Best day: {best_day['count']} contributions "
    f"on {best_day['date']}"
)
print("========================================")