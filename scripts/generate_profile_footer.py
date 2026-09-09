from pathlib import Path
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT=Path(os.environ.get('OUT_DIR','assets/animated')); OUT.mkdir(parents=True,exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'
def F(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)
def bg(w,h):
    im=Image.new('RGB',(w,h),(6,10,18)); d=ImageDraw.Draw(im)
    for x in range(0,w,36): d.line((x,0,x,h),fill=(45,59,80),width=1)
    for y in range(0,h,28): d.line((0,y,w,y),fill=(45,59,80),width=1)
    return im.convert('RGBA')
def save(frames,path):
    pal=frames[0].convert('RGB').quantize(colors=96); q=[x.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE) for x in frames]
    q[0].save(path,save_all=True,append_images=q[1:],duration=100,loop=0,optimize=True,disposal=2)
frames=[]
for i in range(18):
    im=bg(1200,110); d=ImageDraw.Draw(im); phase=i*math.pi/9
    for x in range(0,1200,24):
        y=78+int(16*math.sin(x/92+phase)); d.ellipse((x,y,x+4,y+4),fill=(56,189,248))
    title='gODtECH'; w=d.textlength(title,font=F(25,True)); d.text(((1200-w)/2,23),title,font=F(25,True),fill=(248,250,252))
    sub='BUILD · MEASURE · ITERATE'; w=d.textlength(sub,font=F(10,True)); d.text(((1200-w)/2,60),sub,font=F(10,True),fill=(100,116,139))
    frames.append(im)
save(frames,OUT/'footer.gif')
