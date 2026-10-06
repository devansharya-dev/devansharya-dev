from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import html

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "source-prepped.png"
OUTPUT = ROOT / "avi-ascii.svg"

RAMP = " .:-=+*#%@"

COLS = 100
CHAR_WIDTH = 8
CHAR_HEIGHT = 12

ROW_DELAY = 0.045
ROW_DURATION = 0.35

if not INPUT.exists():
    raise FileNotFoundError(f"Missing: {INPUT}")

img = Image.open(INPUT).convert("L")

# --------------------------------------------------
# 1. Crop the white background
# --------------------------------------------------

threshold = 242

mask = img.point(
    lambda p: 255 if p < threshold else 0
)

bbox = mask.getbbox()

if bbox:
    left, top, right, bottom = bbox

    pad_x = int((right - left) * 0.03)
    pad_y = int((bottom - top) * 0.03)

    left = max(0, left - pad_x)
    top = max(0, top - pad_y)
    right = min(img.width, right + pad_x)
    bottom = min(img.height, bottom + pad_y)

    img = img.crop(
        (left, top, right, bottom)
    )

# --------------------------------------------------
# 2. Improve contrast
# --------------------------------------------------

img = ImageOps.autocontrast(
    img,
    cutoff=1
)

img = ImageEnhance.Contrast(
    img
).enhance(1.15)

# --------------------------------------------------
# 3. Resize
# --------------------------------------------------

aspect = img.height / img.width

rows = max(
    1,
    int(COLS * aspect * 0.52)
)

img = img.resize(
    (COLS, rows),
    Image.Resampling.LANCZOS
)

pixels = img.load()

# --------------------------------------------------
# 4. Convert pixels -> ASCII
# --------------------------------------------------

lines = []

for y in range(rows):

    line = ""

    for x in range(COLS):

        brightness = pixels[x, y]

        # White background becomes empty space
        if brightness >= 238:
            line += " "
            continue

        # Normalize dark pixels
        value = (238 - brightness) / 238

        # Gamma keeps facial details visible
        value = value ** 0.72

        index = int(
            value * (len(RAMP) - 1)
        )

        index = max(
            0,
            min(len(RAMP) - 1, index)
        )

        line += RAMP[index]

    lines.append(
        line.rstrip()
    )

# --------------------------------------------------
# 5. SVG
# --------------------------------------------------

width = COLS * CHAR_WIDTH
height = rows * CHAR_HEIGHT + 10

svg = []

svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{width}" '
    f'height="{height}" '
    f'viewBox="0 0 {width} {height}">'
)

svg.append("""
<style>
.ascii {
    font-family: "Courier New", monospace;
    font-size: 12px;
    font-weight: 700;
    fill: #c9d1d9;
    white-space: pre;
}
</style>
""")

for y, line in enumerate(lines):

    if not line.strip():
        continue

    yy = (y + 1) * CHAR_HEIGHT

    delay = y * ROW_DELAY

    svg.append(
        f"""
<clipPath id="row{y}">
    <rect
        x="0"
        y="{y * CHAR_HEIGHT}"
        width="0"
        height="{CHAR_HEIGHT + 2}"
    >
        <animate
            attributeName="width"
            from="0"
            to="{width}"
            dur="{ROW_DURATION}s"
            begin="{delay}s"
            fill="freeze"
        />
    </rect>
</clipPath>
"""
    )

    safe = html.escape(line)

    svg.append(
        f"""
<g clip-path="url(#row{y})">
    <text
        x="0"
        y="{yy}"
        class="ascii"
    >{safe}</text>
</g>
"""
    )

svg.append("</svg>")

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)

print("Created:", OUTPUT)
print("Columns:", COLS)
print("Rows:", rows)
print("Size:", width, "x", height)