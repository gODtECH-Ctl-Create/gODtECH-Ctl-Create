from __future__ import annotations

import json
import math
import os
import random
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(os.environ.get("OUT_DIR", "assets/animated"))
OUT.mkdir(parents=True, exist_ok=True)
random.seed(17)

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
            px[x, y] = (int(6 + 8 * t), int(10 + 12 * t + 5 * u), int(18 + 17 * t + 9 * u))
    return im


def grid(draw: ImageDraw.ImageDraw, w: int, h: int, step: int = 24):
    for x in range(0, w, step):
        draw.line((x, 0, x, h), fill=(54, 67, 89), width=1)
    for y in range(0, h, step):
        draw.line((0, y, w, y), fill=(54, 67, 89), width=1)


def glow_dot(im: Image.Image, x: float, y: float, color, radius: int = 5):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*color, 220))
    im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(radius * 2)))
    im.alpha_composite(layer)


def palette(frames, colors=96):
    samples = []
    for frame in frames[::max(1, len(frames) // 6)]:
        sample = frame.convert("RGB").copy()
        sample.thumbnail((300, 120))
        samples.append(sample)
    sw = max(x.width for x in samples)
    sh = max(x.height for x in samples)
    sheet = Image.new("RGB", (sw * len(samples), sh), (6, 10, 18))
    for i, sample in enumerate(samples):
        sheet.paste(sample, (i * sw, 0))
    return sheet.quantize(colors=colors)


def save_gif(frames, path: Path, duration=120):
    pal = palette(frames)
    quantized = [f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    quantized[0].save(path, save_all=True, append_images=quantized[1:], duration=duration, loop=0, optimize=True, disposal=2)


def intro():
    W, H, N = 900, 120, 18
    lines = [
        "PRODUCT MANAGER  ·  PRODUCT BUILDER  ·  SYSTEMS THINKER",
        "Turning ideas into products, systems, and evidence",
        "Building useful technology for Nigeria, Africa, and the real world",
    ]
    frames = []
    for i in range(N):
        im = background(W, H).convert("RGBA")
        d = ImageDraw.Draw(im)
        grid(d, W, H, 30)
        sx = -180 + i * 72
        d.rectangle((sx, 0, sx + 90, H), fill=(56, 189, 248, 22))
        d.text((34, 16), "GOTEK // PROFILE SIGNAL", font=font(9), fill=(100, 116, 139))
        for j, line in enumerate(lines):
            size = 14 if j == 0 else 12
            y = 41 + j * 23
            shown = line[:min(len(line), max(0, int(i * 4.8 - j * 13)))]
            d.text((34, y), shown, font=font(size, j == 0), fill=(248, 250, 252) if j == 0 else (148, 163, 184))
            if len(shown) < len(line):
                cw = d.textlength(shown, font=font(size, j == 0))
                d.rectangle((35 + cw, y + 2, 38 + cw, y + size + 1), fill=(56, 189, 248))
        frames.append(im)
    save_gif(frames, OUT / "intro.gif", 100)


def system_hero():
    W, H, N = 900, 240, 20
    items = [
        ("PRODUCT", "problem → scope", (167, 139, 250)),
        ("SYSTEM", "data → logic", (56, 189, 248)),
        ("AI / AUTOMATION", "signals → leverage", (34, 197, 94)),
        ("EVIDENCE", "measure → learn", (245, 158, 11)),
        ("ITERATE", "ship → repeat", (244, 114, 182)),
    ]
    xs, y = [62, 255, 450, 645, 838], 150
    frames = []
    for i in range(N):
        im = background(W, H).convert("RGBA")
        d = ImageDraw.Draw(im)
        grid(d, W, H)
        d.text((38, 36), "GOTEK // PRODUCT SYSTEMS LAB", font=font(9), fill=(100, 116, 139))
        d.text((38, 65), "SYSTEMS IN MOTION", font=font(27, True), fill=(248, 250, 252))
        d.text((38, 88), "ideas become products, products become systems, systems produce evidence", font=font(10), fill=(148, 163, 184))
        d.line((50, y, 850, y), fill=(46, 58, 78), width=4)
        shift = (i * 18) % 28
        for k in range(35):
            x = 50 + k * 27 - shift
            if 50 < x < 850:
                d.line((x, y, x + 11, y), fill=(56, 189, 248), width=3)
        for idx, (label, sub, col) in enumerate(items):
            yy = y + int(math.sin(i * 0.42 + idx) * 5)
            x = xs[idx]
            d.ellipse((x - 11, yy - 11, x + 11, yy + 11), fill=(11, 18, 32), outline=col, width=2)
            glow_dot(im, x, yy, col, 4)
            d = ImageDraw.Draw(im)
            d.text((x - d.textlength(label, font=font(9, True)) / 2, yy + 27), label, font=font(9, True), fill=(248, 250, 252))
            d.text((x - d.textlength(sub, font=font(7)) / 2, yy + 43), sub, font=font(7), fill=(100, 116, 139))
        frames.append(im)
    save_gif(frames, OUT / "gotek-system.gif", 120)


def project_orbit():
    W, H, N = 900, 270, 24
    projects = [
        ("SAYRR", "VOICE / INPUT", (167, 139, 250)), ("MORTGAGEOPS", "FINANCIAL", (56, 189, 248)),
        ("TECHTRACK", "LEARNING", (34, 197, 94)), ("LEAD ENGINE", "RECRUITMENT", (245, 158, 11)),
        ("ABEMAIL MAIL", "BUSINESS EMAIL", (244, 114, 182)), ("PROQUREMENT", "CONSTRUCTION", (56, 189, 248)),
        ("ABE TECHLAB OPS", "INTERNAL", (34, 197, 94)), ("CLOUD INFRA", "PLATFORM", (167, 139, 250)),
    ]
    center = (450, 137)
    frames = []
    for i in range(N):
        im = background(W, H).convert("RGBA")
        d = ImageDraw.Draw(im)
        grid(d, W, H, 22)
        d.text((34, 28), "ACTIVE PORTFOLIO / SYSTEMS ORBIT", font=font(9), fill=(100, 116, 139))
        for rx, ry in [(150, 62), (240, 95), (335, 118)]:
            d.ellipse((center[0]-rx, center[1]-ry, center[0]+rx, center[1]+ry), outline=(71, 85, 105), width=1)
        a = math.radians(i * 12)
        for rx, ry, col, direction in [(335, 118, (56, 189, 248), 1), (240, 95, (167, 139, 250), -1)]:
            aa = a * direction
            glow_dot(im, center[0] + rx * math.cos(aa), center[1] + ry * math.sin(aa), col, 4)
        d = ImageDraw.Draw(im)
        d.ellipse((center[0]-43, center[1]-43, center[0]+43, center[1]+43), fill=(11, 18, 32), outline=(56, 189, 248), width=2)
        d.ellipse((center[0]-8, center[1]-8, center[0]+8, center[1]+8), fill=(248, 250, 252))
        d.text((center[0]-34, center[1]+55), "gODtECH", font=font(10, True), fill=(248, 250, 252))
        d.text((center[0]-48, center[1]+71), "PRODUCT STUDIO", font=font(7), fill=(100, 116, 139))
        angles = [-160, -115, -75, -30, 22, 72, 125, 160]
        for idx, (name, sub, col) in enumerate(projects):
            ang = math.radians(angles[idx] + i * (1.0 if idx % 2 == 0 else -0.7))
            rr = [335, 240, 240, 335, 335, 240, 240, 335][idx]
            ry = [118, 95, 95, 118, 118, 95, 95, 118][idx]
            x = center[0] + rr * math.cos(ang); yy = center[1] + ry * math.sin(ang)
            cw = 128 if len(name) < 13 else 145
            d.rounded_rectangle((x-cw/2, yy-18, x+cw/2, yy+18), radius=9, fill=(11,18,32), outline=col, width=2)
            d.text((x-cw/2+9, yy-10), name, font=font(8, True), fill=(248,250,252))
            d.text((x-cw/2+9, yy+2), sub, font=font(6), fill=(100,116,139))
        frames.append(im)
    save_gif(frames, OUT / "project-orbit.gif", 110)


def build_loop():
    W, H, N = 900, 155, 20
    steps = [("PROBLEM", (167,139,250)), ("PRODUCT", (56,189,248)), ("SYSTEM", (34,197,94)), ("EVIDENCE", (245,158,11)), ("ITERATE", (244,114,182))]
    xs, y = [58, 255, 450, 645, 842], 92
    frames = []
    for i in range(N):
        im = background(W,H).convert("RGBA"); d=ImageDraw.Draw(im); grid(d,W,H,30)
        d.text((38,27),"BUILDING LOOP / EXECUTION MODEL",font=font(9),fill=(100,116,139))
        d.text((38,50),"Problem → Product → System → Evidence → Iteration",font=font(17,True),fill=(248,250,252))
        d.line((50,y,850,y),fill=(46,58,78),width=4)
        shift=(i*21)%34
        for k in range(35):
            x=50+k*27-shift
            if 50<x<850: d.line((x,y,x+10,y),fill=(56,189,248),width=3)
        glow_dot(im,50+(i/(N-1))*800,y,(56,189,248),5)
        d=ImageDraw.Draw(im)
        for idx,(lab,col) in enumerate(steps):
            x=xs[idx]
            d.ellipse((x-15,y-15,x+15,y+15),fill=(11,18,32),outline=col,width=2)
            d.ellipse((x-5,y-5,x+5,y+5),fill=col)
            tw=d.textlength(lab,font=font(8,True)); d.text((x-tw/2,y+27),lab,font=font(8,True),fill=(248,250,252))
        frames.append(im)
    save_gif(frames,OUT/"build-loop.gif",120)


def tech_stream():
    W,H,N=900,135,20
    tech=[("TypeScript",(167,139,250)),("React",(56,189,248)),("Next.js",(56,189,248)),("Node.js",(34,197,94)),("PostgreSQL",(34,197,94)),("Supabase",(56,189,248)),("Docker",(167,139,250)),("GitHub Actions",(245,158,11))]
    frames=[]
    for i in range(N):
        im=background(W,H).convert("RGBA"); d=ImageDraw.Draw(im); grid(d,W,H,30)
        d.text((38,25),"TECHNOLOGY STREAM / BUILD SURFACE",font=font(8),fill=(100,116,139))
        d.text((38,47),"The stack changes. The engineering principles don't.",font=font(16,True),fill=(248,250,252))
        y=83; d.line((40,y,860,y),fill=(46,58,78),width=4)
        for k in range(36):
            x=40+k*25-(i*17%25)
            if 40<x<860: d.line((x,y,x+10,y),fill=(56,189,248),width=3)
        for idx,(name,col) in enumerate(tech):
            x=44+idx*106; yy=y-19+int(math.sin(i*.35+idx)*3)
            d.rounded_rectangle((x,yy,x+94,yy+38),radius=9,fill=(11,18,32),outline=col,width=2)
            d.text((x+9,yy+12),name,font=font(8 if len(name)>12 else 9),fill=(248,250,252))
        frames.append(im)
    save_gif(frames,OUT/"tech-stream.gif",120)


def contribution_data():
    url = "https://github-contributions-api.jogruber.de/v4/gODtECH-Ctl-Create?y=last"
    with urlopen(url, timeout=20) as response:
        payload = json.load(response)
    by_date = {item["date"]: item for item in payload.get("contributions", [])}
    end = date.today()
    start = end - timedelta(days=364)
    data=[]
    for n in range(365):
        day = start + timedelta(days=n)
        item = by_date.get(day.isoformat(), {"date":day.isoformat(),"count":0,"level":0})
        data.append((day,item.get("count",0),int(item.get("level",0))))
    return data


def heatmap():
    try:
        data = contribution_data()
    except Exception as exc:
        print(f"Contribution API unavailable: {exc}")
        return
    W,H,N = 900,230,24
    cell, gap = 11, 3
    left, top = 38, 74
    levels=[(20,27,39),(24,74,51),(34,125,73),(45,180,95),(74,222,128)]
    frames=[]
    max_level=max((lvl for _,_,lvl in data),default=0)
    for i in range(N):
        im=background(W,H).convert("RGBA"); d=ImageDraw.Draw(im); grid(d,W,H,30)
        d.text((38,26),"LIVE CONTRIBUTION HEATMAP / LAST 365 DAYS",font=font(10),fill=(100,116,139))
        d.text((38,47),"real GitHub contribution intensity · refreshed automatically",font=font(9),fill=(148,163,184))
        # GitHub-style weekday rows, seven rows and 53 columns.
        for idx,(day,count,level) in enumerate(data):
            col = idx // 7
            row = idx % 7
            x = left + col*(cell+gap); y = top + row*(cell+gap)
            fill = levels[min(level,4)]
            d.rounded_rectangle((x,y,x+cell,y+cell),radius=2,fill=fill)
            # moving scan highlight only; no synthetic activity is added.
            scan_col = int((i / N) * 53)
            if col == scan_col:
                d.rounded_rectangle((x-2,y-2,x+cell+2,y+cell+2),radius=3,outline=(248,250,252),width=1)
        d.text((left, 180),"LESS",font=font(8),fill=(100,116,139))
        lx=83
        for level,fill in enumerate(levels):
            d.rounded_rectangle((lx,176,lx+cell,187),radius=2,fill=fill); lx+=cell+gap+3
        d.text((left,202),"MORE",font=font(8),fill=(100,116,139))
        # Total based on fetched real data.
        total=sum(c for _,c,_ in data)
        d.text((W-285,47),f"{total:,} contributions",font=font(11,True),fill=(248,250,252))
        frames.append(im)
    save_gif(frames,OUT/"contribution-heatmap.gif",110)


if __name__ == "__main__":
    intro()
    system_hero()
    project_orbit()
    build_loop()
    tech_stream()
    heatmap()
