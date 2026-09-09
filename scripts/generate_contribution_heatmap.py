from __future__ import annotations

import json
import math
import os
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(os.environ.get("OUT_DIR", "assets/animated"))
OUT.mkdir(parents=True, exist_ok=True)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def background(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            t = x / w
            u = y / h
            px[x, y] = (
                int(6 + 8 * t),
                int(10 + 12 * t + 5 * u),
                int(18 + 17 * t + 9 * u),
            )
    return im


def grid(draw: ImageDraw.ImageDraw, w: int, h: int, step: int = 30):
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(54, 67, 89), width=1)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(54, 67, 89), width=1)


def glow(im: Image.Image, x: float, y: float, color, radius: int = 5):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(*color, 210))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 2)))
    im.alpha_composite(layer)


def save_gif(frames: list[Image.Image], path: Path, duration: int = 110):
    samples = []
    for frame in frames[::max(1, len(frames) // 6)]:
        sample = frame.convert("RGB").copy()
        sample.thumbnail((320, 120))
        samples.append(sample)
    sheet = Image.new("RGB", (max(s.width for s in samples) * len(samples), max(s.height for s in samples)), (6, 10, 18))
    for i, sample in enumerate(samples):
        sheet.paste(sample, (i * sample.width, 0))
    palette = sheet.quantize(colors=96)
    quantized = [frame.convert("RGB").quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def fetch_contributions() -> tuple[date, date, dict[date, tuple[int, int]]]:
    url = "https://github-contributions-api.jogruber.de/v4/gODtECH-Ctl-Create?y=last"
    with urlopen(url, timeout=20) as response:
        payload = json.load(response)

    by_date: dict[date, tuple[int, int]] = {}
    for item in payload.get("contributions", []):
        day = date.fromisoformat(item["date"])
        by_date[day] = (int(item.get("count", 0)), int(item.get("level", 0)))

    end = date.today()
    raw_start = end - timedelta(days=364)
    # GitHub-style columns begin on Sunday.
    start = raw_start - timedelta(days=(raw_start.weekday() + 1) % 7)
    return start, end, by_date


def main():
    try:
        start, end, by_date = fetch_contributions()
    except Exception as exc:
        print(f"Contribution API unavailable: {exc}")
        return

    days = (end - start).days + 1
    columns = math.ceil(days / 7)

    cell = 11
    gap = 3
    left = 62
    top = 70
    bottom = 37
    right = 160
    width = max(900, left + columns * (cell + gap) + right)
    height = top + 7 * (cell + gap) + bottom
    frames = []

    levels = [
        (24, 32, 45),
        (23, 72, 48),
        (32, 117, 67),
        (43, 166, 91),
        (74, 222, 128),
    ]

    total = sum(value[0] for value in by_date.values() if start <= next((d for d in by_date if by_date[d] == value), end) <= end)
    # The API payload is already scoped to the requested year window. Use the visible calendar window for the displayed total.
    total = 0
    visible: list[tuple[date, int, int, int, int]] = []
    day = start
    while day <= end:
        count, level = by_date.get(day, (0, 0))
        delta = (day - start).days
        col = delta // 7
        row = (day.weekday() + 1) % 7  # Sunday=0 ... Saturday=6
        visible.append((day, count, level, col, row))
        total += count
        day += timedelta(days=1)

    month_positions: dict[int, str] = {}
    previous_month = None
    for day, _, _, col, _ in visible:
        if day.month != previous_month:
            month_positions[col] = day.strftime("%b").upper()
            previous_month = day.month

    for frame_no in range(24):
        im = background(width, height).convert("RGBA")
        draw = ImageDraw.Draw(im)
        grid(draw, width, height)

        draw.text((38, 23), "LIVE CONTRIBUTION HEATMAP / LAST 365 DAYS", font=font(10), fill=(100, 116, 139))
        draw.text((38, 43), "real public GitHub contribution history · animated scan", font=font(9), fill=(148, 163, 184))
        draw.text((width - 210, 25), f"{total:,} contributions", font=font(11, True), fill=(248, 250, 252))

        for col, label in month_positions.items():
            x = left + col * (cell + gap)
            draw.text((x, 55), label, font=font(7), fill=(100, 116, 139))

        weekdays = [("SUN", 0), ("MON", 1), ("WED", 3), ("FRI", 5)]
        for label, row in weekdays:
            y = top + row * (cell + gap) + 1
            draw.text((6, y), label, font=font(6), fill=(71, 85, 105))

        scan_col = frame_no % columns
        for day, count, level, col, row in visible:
            x = left + col * (cell + gap)
            y = top + row * (cell + gap)
            fill = levels[min(max(level, 0), 4)]
            draw.rounded_rectangle((x, y, x + cell, y + cell), radius=2, fill=fill)
            if col == scan_col:
                draw.rounded_rectangle((x - 2, y - 2, x + cell + 2, y + cell + 2), radius=3, outline=(248, 250, 252), width=1)
                glow(im, x + cell / 2, y + cell / 2, (56, 189, 248), 3)

        legend_y = height - 25
        draw.text((left, legend_y), "LESS", font=font(7), fill=(100, 116, 139))
        lx = left + 36
        for fill in levels:
            draw.rounded_rectangle((lx, legend_y - 2, lx + cell, legend_y + 9), radius=2, fill=fill)
            lx += cell + gap + 4
        draw.text((lx + 2, legend_y), "MORE", font=font(7), fill=(100, 116, 139))

        frames.append(im)

    save_gif(frames, OUT / "contribution-heatmap.gif")


if __name__ == "__main__":
    main()
