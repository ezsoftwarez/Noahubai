#!/usr/bin/env python3
"""Generate REDRUM app icons and splash screens for the Android/Capacitor project.

Regenerate after a branding change with:
    python3 scripts/generate_assets.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "android", "app", "src", "main", "res")
FONT_PATH = "/mnt/skills/examples/canvas-design/canvas-fonts/Outfit-Bold.ttf"

BG = (10, 10, 15, 255)          # #0a0a0f
ACCENT_A = (224, 41, 62, 255)   # #e0293e
ACCENT_B = (122, 22, 32, 255)   # #7a1620
WHITE = (245, 245, 248, 255)

LEGACY_SIZES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
FOREGROUND_SIZES = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
SPLASH_PORT = {
    "mdpi": (320, 480), "hdpi": (480, 800), "xhdpi": (720, 1280),
    "xxhdpi": (960, 1600), "xxxhdpi": (1280, 1920),
}
SPLASH_LAND = {
    "mdpi": (480, 320), "hdpi": (800, 480), "xhdpi": (1280, 720),
    "xxhdpi": (1600, 960), "xxxhdpi": (1920, 1280),
}


def diagonal_gradient(size, c1, c2):
    """Simple diagonal (top-left -> bottom-right) linear gradient square."""
    base = Image.new("RGBA", (size, size), c1)
    top = Image.new("RGBA", (size, size), c2)
    mask = Image.new("L", (size, size))
    md = mask.load()
    for y in range(size):
        for x in range(size):
            md[x, y] = int(255 * ((x + y) / (2 * size)))
    return Image.composite(top, base, mask)


def rounded_mask(size, radius_ratio):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    r = int(size * radius_ratio)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return mask


def draw_r_glyph(canvas, cx, cy, glyph_size, color=WHITE):
    font = ImageFont.truetype(FONT_PATH, glyph_size)
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), "R", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), "R", font=font, fill=color)


def make_mark(size, inset_ratio=0.0, radius_ratio=0.22, transparent_bg=False):
    """A rounded-square gradient mark with the R glyph, at `size`px, with
    `inset_ratio` of transparent padding on each side (for adaptive icons)."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    inset = int(size * inset_ratio)
    mark_size = size - 2 * inset
    grad = diagonal_gradient(mark_size, ACCENT_A, ACCENT_B)
    mask = rounded_mask(mark_size, radius_ratio)
    if not transparent_bg:
        bg = Image.new("RGBA", (size, size), BG)
        canvas = bg
    canvas.paste(grad, (inset, inset), mask)
    draw_r_glyph(canvas, size / 2, size / 2, int(mark_size * 0.58))
    return canvas


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT))


def generate_launcher_icons():
    for density, size in LEGACY_SIZES.items():
        icon = make_mark(size, inset_ratio=0.0, radius_ratio=0.22, transparent_bg=False)
        save(icon, os.path.join(RES, f"mipmap-{density}", "ic_launcher.png"))

        round_icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circle_mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circle_mask).ellipse([0, 0, size - 1, size - 1], fill=255)
        round_icon.paste(icon, (0, 0), circle_mask)
        save(round_icon, os.path.join(RES, f"mipmap-{density}", "ic_launcher_round.png"))

    for density, size in FOREGROUND_SIZES.items():
        fg = make_mark(size, inset_ratio=0.20, radius_ratio=0.22, transparent_bg=True)
        save(fg, os.path.join(RES, f"mipmap-{density}", "ic_launcher_foreground.png"))


def make_splash(w, h):
    img = Image.new("RGBA", (w, h), BG)
    draw = ImageDraw.Draw(img)

    # soft radial-ish glow behind the mark using concentric translucent circles
    cx, cy = w // 2, int(h * 0.44)
    glow_r = int(min(w, h) * 0.42)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    steps = 40
    for i in range(steps, 0, -1):
        r = int(glow_r * i / steps)
        alpha = int(70 * (1 - i / steps))
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(224, 41, 62, alpha))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    mark_size = int(min(w, h) * 0.24)
    mark = make_mark(mark_size, inset_ratio=0.0, radius_ratio=0.22, transparent_bg=True)
    img.paste(mark, (cx - mark_size // 2, cy - mark_size // 2), mark)

    font_size = int(min(w, h) * 0.075)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = "REDRUM"
    # letter-spacing by drawing char by char
    spacing = int(font_size * 0.28)
    bbox_total = draw.textbbox((0, 0), text, font=font)
    widths = [draw.textbbox((0, 0), ch, font=font)[2] for ch in text]
    total_w = sum(widths) + spacing * (len(text) - 1)
    x = cx - total_w / 2
    ty = cy + mark_size * 0.72
    for ch, cw in zip(text, widths):
        draw.text((x, ty), ch, font=font, fill=WHITE)
        x += cw + spacing

    sub_font = ImageFont.truetype(FONT_PATH, int(font_size * 0.34))
    sub = "NOAHUBAI AI HUB"
    sub_bbox = draw.textbbox((0, 0), sub, font=sub_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text((cx - sub_w / 2, ty + font_size * 1.25), sub, font=sub_font, fill=(148, 148, 168, 255))

    return img.convert("RGB")


def generate_splash():
    for density, (w, h) in SPLASH_PORT.items():
        save(make_splash(w, h), os.path.join(RES, f"drawable-port-{density}", "splash.png"))
    for density, (w, h) in SPLASH_LAND.items():
        save(make_splash(w, h), os.path.join(RES, f"drawable-land-{density}", "splash.png"))
    # default drawable/splash.png (used pre-density-match fallback)
    save(make_splash(*SPLASH_PORT["mdpi"]), os.path.join(RES, "drawable", "splash.png"))


if __name__ == "__main__":
    generate_launcher_icons()
    generate_splash()
    print("Done.")
