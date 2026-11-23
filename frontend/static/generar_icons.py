from PIL import Image, ImageDraw
from pathlib import Path

Path("frontend/static/icons").mkdir(parents=True, exist_ok=True)
for size in (192, 512):
    img = Image.new("RGB", (size, size), "#153b2c")
    d = ImageDraw.Draw(img)
    m = size // 4
    d.ellipse([m, m, size - m, size - m], fill="#45d483")
    img.save(f"frontend/static/icons/icon-{size}.png")