"""
Generate placeholder app icons for Baby Cry App.
Run: python3 scripts/generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT, exist_ok=True)

BG      = (255, 107, 107)   # #FF6B6B  brand red
FG      = (255, 255, 255)   # white


def draw_icon(size, padding_ratio=0.2):
    img  = Image.new('RGB', (size, size), BG)
    draw = ImageDraw.Draw(img)

    # baby emoji-style silhouette: simple circle head + body
    pad  = int(size * padding_ratio)
    cx, cy = size // 2, size // 2

    # head
    hr = int(size * 0.22)
    draw.ellipse([cx - hr, cy - hr - int(size*0.10),
                  cx + hr, cy + hr - int(size*0.10)], fill=FG)

    # body arc
    bw = int(size * 0.30)
    bh = int(size * 0.22)
    by = cy + int(size * 0.14)
    draw.ellipse([cx - bw, by, cx + bw, by + bh * 2], fill=FG)

    # sound waves (two arcs to the right)
    wc = (cx + int(size*0.28), cy - int(size*0.06))
    for r_offset, width in [(0.12, 3), (0.20, 2)]:
        r = int(size * (0.14 + r_offset))
        box = [wc[0] - r, wc[1] - r, wc[0] + r, wc[1] + r]
        draw.arc(box, start=-60, end=60, fill=BG, width=max(2, int(size*0.025)))

    return img


def make_icon(path, size):
    img = draw_icon(size)
    img.save(path, 'PNG')
    print(f'  {path}  ({size}x{size})')


def make_splash(path, w=1284, h=2778):
    img  = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    icon_size = min(w, h) // 4
    icon = draw_icon(icon_size)
    x = (w - icon_size) // 2
    y = (h - icon_size) // 2 - int(h * 0.05)
    img.paste(icon, (x, y))
    img.save(path, 'PNG')
    print(f'  {path}  ({w}x{h})')


print('Generating icons...')
make_icon(os.path.join(OUT, 'icon.png'), 1024)
make_icon(os.path.join(OUT, 'adaptive-icon.png'), 1024)
make_icon(os.path.join(OUT, 'favicon.png'), 196)
make_splash(os.path.join(OUT, 'splash.png'))
print('Done.')
