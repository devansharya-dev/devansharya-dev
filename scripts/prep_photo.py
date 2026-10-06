from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "source-photo.png"
OUTPUT = ROOT / "source-prepped.png"

if not INPUT.exists():
    print(f"File not found: {INPUT}")
    sys.exit(1)

print("Removing background...")

input_image = Image.open(INPUT).convert("RGBA")
subject = remove(input_image)

rgba = np.array(subject)

alpha = rgba[:, :, 3]
rgb = rgba[:, :, :3]

gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

clahe = cv2.createCLAHE(
    clipLimit=2.0,
    tileGridSize=(8, 8)
)

gray = clahe.apply(gray)

alpha_mask = alpha.astype(np.float32) / 255.0

white = np.full_like(gray, 255)

result = (
    gray * alpha_mask +
    white * (1 - alpha_mask)
).astype(np.uint8)

Image.fromarray(result, mode="L").save(OUTPUT)

print(f"Created: {OUTPUT}")