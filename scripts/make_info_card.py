from pathlib import Path
import html

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "info-card.svg"

WIDTH = 490
HEIGHT = 500

BG = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
GREEN = "#3fb950"
BORDER = "#30363d"

lines = [
    ("label", "devansh@github"),
    ("divider", "────────────────────────────────────"),
    ("space", ""),
    ("key", "Role        ", "Full Stack Developer"),
    ("key", "Focus       ", "Web • Software Development • AI"),
    ("space", ""),
    ("key", "Frontend    ", "React • Tailwind • GSAP"),
    ("key", "Backend     ", "Node • Express • PostgreSQL"),
    ("key", "Tools       ", "Docker • n8n • Git"),
    ("key", "Languages   ", "JavaScript • Python"),
    ("space", ""),
    ("section", "Building"),
    ("bullet", "Fast & maintainable applications"),
    ("bullet", "AI-powered software"),
    ("bullet", "Production-ready systems"),
]

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}">

    <rect width="100%" height="100%" rx="14"
          fill="{BG}"
          stroke="{BORDER}"
          stroke-width="1"/>
    '''
)

# Terminal dots
svg.append("""
<circle cx="22" cy="22" r="5" fill="#ff5f56"/>
<circle cx="40" cy="22" r="5" fill="#ffbd2e"/>
<circle cx="58" cy="22" r="5" fill="#27c93f"/>
""")

y = 58
line_index = 0

for item in lines:

    kind = item[0]

    if kind == "space":
        y += 18
        continue

    delay = line_index * 0.10

    if kind == "label":

        text = html.escape(item[1])

        svg.append(
            f'''
<text x="22" y="{y}"
      font-family="monospace"
      font-size="20"
      font-weight="700"
      fill="{GREEN}"
      opacity="0">
    {text}
    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.35s"
             begin="{delay}s"
             fill="freeze"/>
</text>
'''
        )

    elif kind == "divider":

        text = html.escape(item[1])

        svg.append(
            f'''
<text x="22" y="{y}"
      font-family="monospace"
      font-size="13"
      fill="{BORDER}"
      opacity="0">
    {text}
    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.3s"
             begin="{delay}s"
             fill="freeze"/>
</text>
'''
        )

    elif kind == "key":

        key = html.escape(item[1])
        value = html.escape(item[2])

        svg.append(
            f'''
<text x="24" y="{y}"
      font-family="monospace"
      font-size="13"
      fill="{MUTED}"
      opacity="0">
    {key}
    <tspan fill="{TEXT}">{value}</tspan>

    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.35s"
             begin="{delay}s"
             fill="freeze"/>
</text>
'''
        )

    elif kind == "section":

        text = html.escape(item[1])

        svg.append(
            f'''
<text x="24" y="{y}"
      font-family="monospace"
      font-size="15"
      font-weight="700"
      fill="{ACCENT}"
      opacity="0">
    {text}

    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.35s"
             begin="{delay}s"
             fill="freeze"/>
</text>
'''
        )

    elif kind == "bullet":

        text = html.escape(item[1])

        svg.append(
            f'''
<text x="24" y="{y}"
      font-family="monospace"
      font-size="13"
      fill="{TEXT}"
      opacity="0">
    <tspan fill="{GREEN}">→</tspan>
    <tspan dx="8">{text}</tspan>

    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.35s"
             begin="{delay}s"
             fill="freeze"/>
</text>
'''
        )

    y += 27
    line_index += 1

# Footer quote
footer_y = HEIGHT - 58

svg.append(
    f'''
<text x="24" y="{footer_y}"
      font-family="monospace"
      font-size="11"
      fill="{MUTED}"
      opacity="0">
    "Not just visually appealing."
    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.5s"
             begin="2.0s"
             fill="freeze"/>
</text>

<text x="24" y="{footer_y + 18}"
      font-family="monospace"
      font-size="11"
      fill="{MUTED}"
      opacity="0">
    "Built to be production-ready."
    <animate attributeName="opacity"
             from="0"
             to="1"
             dur="0.5s"
             begin="2.1s"
             fill="freeze"/>
</text>
'''
)

svg.append("</svg>")

OUTPUT.write_text(
    "\n".join(svg),
    encoding="utf-8"
)

print(f"Created: {OUTPUT}")