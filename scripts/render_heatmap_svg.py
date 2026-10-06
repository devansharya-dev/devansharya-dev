from pathlib import Path
from datetime import datetime, timedelta
import json
import html

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "contrib-heatmap.svg"

CELL = 12
GAP = 4

LEFT = 38
TOP = 42
RIGHT = 20
BOTTOM = 48

COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

if not INPUT.exists():
    raise FileNotFoundError(f"Missing: {INPUT}")

data = json.loads(INPUT.read_text(encoding="utf-8"))

days = data["days"]
stats = data["stats"]

date_map = {
    day["date"]: day
    for day in days
}

latest_date = datetime.strptime(
    days[-1]["date"],
    "%Y-%m-%d"
).date()

start_date = latest_date - timedelta(days=370)

# Align start to Sunday
start_date -= timedelta(
    days=(start_date.weekday() + 1) % 7
)

dates = []

current = start_date

for _ in range(371):
    dates.append(current)
    current += timedelta(days=1)

weeks = (len(dates) + 6) // 7

WIDTH = (
    LEFT
    + weeks * (CELL + GAP)
    + RIGHT
)

HEIGHT = (
    TOP
    + 7 * (CELL + GAP)
    + BOTTOM
)

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

<style>

.title {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Helvetica, Arial, sans-serif;
    font-size: 16px;
    font-weight: 600;
    fill: #c9d1d9;
}}

.month {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Helvetica, Arial, sans-serif;
    font-size: 10px;
    fill: #8b949e;
}}

.weekday {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Helvetica, Arial, sans-serif;
    font-size: 9px;
    fill: #8b949e;
}}

.legend {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 Helvetica, Arial, sans-serif;
    font-size: 9px;
    fill: #8b949e;
}}

.cell {{
    opacity: 0;
}}

</style>
'''
)

# Background
svg.append(
    f'''
<rect
    width="{WIDTH}"
    height="{HEIGHT}"
    rx="14"
    fill="#0d1117"
/>
'''
)

# Title
total = stats["total_contributions"]

svg.append(
    f'''
<text
    x="{LEFT}"
    y="24"
    class="title"
>
    {total} contributions in the last year
</text>
'''
)

# Weekday labels
weekday_labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri",
}

for row, label in weekday_labels.items():

    y = (
        TOP
        + row * (CELL + GAP)
        + CELL - 2
    )

    svg.append(
        f'''
<text
    x="4"
    y="{y}"
    class="weekday"
>
    {label}
</text>
'''
    )

# Month labels
seen_months = set()

for index, date in enumerate(dates):

    column = index // 7

    if date.day <= 7:

        month_key = date.strftime("%Y-%m")

        if month_key in seen_months:
            continue

        seen_months.add(month_key)

        x = (
            LEFT
            + column * (CELL + GAP)
        )

        label = date.strftime("%b")

        svg.append(
            f'''
<text
    x="{x}"
    y="{TOP - 10}"
    class="month"
>
    {html.escape(label)}
</text>
'''
        )

# Contribution cells
for index, date in enumerate(dates):

    column = index // 7
    row = index % 7

    x = (
        LEFT
        + column * (CELL + GAP)
    )

    y = (
        TOP
        + row * (CELL + GAP)
    )

    date_string = date.strftime("%Y-%m-%d")

    day = date_map.get(
        date_string,
        {
            "count": 0,
            "level": 0
        }
    )

    count = day["count"]
    level = max(
        0,
        min(4, day["level"])
    )

    fill = COLORS[level]

    delay = (
        column * 0.018
        + row * 0.035
    )

    tooltip = (
        f"{count} contribution"
        if count == 1
        else f"{count} contributions"
    )

    svg.append(
        f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{fill}"
    class="cell"
>
    <title>
        {html.escape(tooltip)} on {date_string}
    </title>

    <animate
        attributeName="opacity"
        from="0"
        to="1"
        dur="0.35s"
        begin="{delay:.3f}s"
        fill="freeze"
    />

    <animateTransform
        attributeName="transform"
        type="translate"
        from="0 -6"
        to="0 0"
        dur="0.35s"
        begin="{delay:.3f}s"
        fill="freeze"
    />
</rect>
'''
    )

# Legend
legend_y = TOP + 7 * (CELL + GAP) + 22

svg.append(
    f'''
<text
    x="{LEFT}"
    y="{legend_y}"
    class="legend"
>
    Less
</text>
'''
)

legend_start = LEFT + 32

for i, color in enumerate(COLORS):

    x = (
        legend_start
        + i * (CELL + GAP)
    )

    svg.append(
        f'''
<rect
    x="{x}"
    y="{legend_y - 9}"
    width="{CELL}"
    height="{CELL}"
    rx="3"
    fill="{color}"
/>
'''
    )

svg.append(
    f'''
<text
    x="{legend_start + 5 * (CELL + GAP) + 2}"
    y="{legend_y}"
    class="legend"
>
    More
</text>
'''
)

# Stats
stats_text = (
    f"Current streak: {stats['current_streak']}  •  "
    f"Longest streak: {stats['longest_streak']}"
)

svg.append(
    f'''
<text
    x="{WIDTH - RIGHT}"
    y="{legend_y}"
    text-anchor="end"
    class="legend"
>
    {html.escape(stats_text)}
</text>
'''
)

svg.append("</svg>")

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)

print("Created:", OUTPUT)
print("Total:", total)
print("Size:", WIDTH, "x", HEIGHT)