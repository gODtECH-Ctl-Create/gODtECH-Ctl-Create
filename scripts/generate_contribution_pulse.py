from __future__ import annotations

import json, math, os
from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlopen
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT=Path(os.environ.get('OUT_DIR','assets/animated')); OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
def F(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def bg(w,h):
    im=Image.new('RGB',(w,h)); p=im.load()
    for y in range(h):
        for x in range(w):
            t=x/max(1,w-1); u=y/max(1,h-1); p[x,y]=(int(5+7*t),int(9+11*t+4*u),int(16+18*t+7*u))
    return im.convert('RGBA')
def grid(d,w,h,step=32):
    for x in range(0,w,step): d.line((x,0,x,h),fill=(45,59,80),width=1)
    for y in range(0,h,step): d.line((0,y,w,y),fill=(45,59,80),width=1)
def glow(im,x,y,r=6):
    layer=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(layer); d.ellipse((x-r,y-r,x+r,y+r),fill=(56,189,248,220)); im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(r*2))); im.alpha_composite(layer)
def save(frames,path,duration=105):
    q=[x.convert('RGB').quantize(colors=96) for x in frames]; q[0].save(path,save_all=True,append_images=q[1:],duration=duration,loop=0,optimize=True,disposal=2)
def get():
    with urlopen('https://github-contributions-api.jogruber.de/v4/gODtECH-Ctl-Create?y=last',timeout=20) as r: payload=json.load(r)
    by={date.fromisoformat(x['date']):int(x.get('count',0)) for x in payload.get('contributions',[])}
    end=date.today(); start=end-timedelta(days=364); start=start-timedelta(days=(start.weekday()+1)%7)
    days=(end-start).days+1; cols=math.ceil(days/7); weeks=[0]*cols; cur=start
    while cur<=end:
        weeks[(cur-start).days//7]+=by.get(cur,0); cur+=timedelta(days=1)
    return weeks

try: weeks=get()
except Exception as e: print('Contribution API unavailable:',e); raise SystemExit(0)
maxv=max(1,max(weeks))
# Weekly pulse chart
frames=[]; W,H=1200,250; x0,y0,x1,y1=75,80,1140,195
for k in range(24):
    im=bg(W,H); d=ImageDraw.Draw(im); grid(d,W,H)
    d.text((42,22),'CONTRIBUTION PULSE / WEEKLY INTENSITY',font=F(11,True),fill=(100,116,139))
    d.text((42,47),'real contribution history · weekly aggregation · animated scan',font=F(9),fill=(148,163,184))
    pts=[]
    for i,v in enumerate(weeks):
        x=x0+(x1-x0)*i/max(1,len(weeks)-1); y=y1-(y1-y0)*(v/maxv); pts.append((x,y))
    d.polygon([(x0,y1)]+pts+[(x1,y1)],fill=(20,60,58))
    for a,b in zip(pts,pts[1:]): d.line((*a,*b),fill=(56,189,248),width=3)
    for x,y in pts: d.ellipse((x-2,y-2,x+2,y+2),fill=(100,116,139))
    x,y=pts[k%len(pts)]; glow(im,x,y); d=ImageDraw.Draw(im); d.text((42,220),f'PEAK WEEK {maxv:,}',font=F(8,True),fill=(100,116,139))
    frames.append(im)
save(frames,OUT/'contribution-pulse.gif')
# Bar timeline
frames=[]; W,H=1200,230; x0,ybase=70,185; bw=max(6,int(1000/max(1,len(weeks))))
for k in range(24):
    im=bg(W,H); d=ImageDraw.Draw(im); grid(d,W,H)
    d.text((42,22),'CONTRIBUTION LOAD / WEEKLY BARS',font=F(11,True),fill=(100,116,139))
    d.text((42,47),'same real data · another visual layer',font=F(9),fill=(148,163,184))
    for i,v in enumerate(weeks):
        h=int(104*v/maxv); x=x0+i*(bw+3); fill=(56,189,248) if i==k%len(weeks) else (34,110,63)
        d.rounded_rectangle((x,ybase-h,x+bw,ybase),radius=2,fill=fill)
    d.line((65,ybase,1145,ybase),fill=(71,85,105),width=1)
    frames.append(im)
save(frames,OUT/'contribution-bars.gif')
