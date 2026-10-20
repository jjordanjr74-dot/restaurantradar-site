"""Text-free 1920x1920 video backgrounds for Restaurant Radar (renderer overlays headline/sub;
the s*.png cards have baked-in text, which doubled/clipped in the 9x16 crop). Motif centred = crop-safe."""
from PIL import Image, ImageDraw, ImageFilter
import math, random, pathlib
OUT = pathlib.Path(__file__).parent
BG, AMBER, INK = (7, 8, 10), (255, 170, 43), (247, 248, 248)
def base():
    im = Image.new("RGB", (1920, 1920), BG); d = ImageDraw.Draw(im)
    for r in range(120, 1400, 110): d.ellipse([960-r, 760-r, 960+r, 760+r], outline=(30, 32, 36), width=3)
    return im, d
def dots(d, n, seed, col=AMBER, rad=14, spread=520):
    rnd = random.Random(seed)
    for _ in range(n):
        a, r = rnd.random()*6.283, spread*math.sqrt(rnd.random())
        x, y = 960+r*math.cos(a), 760+r*math.sin(a)*0.85
        d.ellipse([x-rad, y-rad, x+rad, y+rad], fill=col)
def sweep(im):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); o = ImageDraw.Draw(ov)
    o.pieslice([960-700, 760-700, 960+700, 760+700], 300, 340, fill=AMBER+(38,))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
def save(im, name): im.filter(ImageFilter.GaussianBlur(0.6)).save(OUT/name); print(name, im.size)
im, d = base(); dots(d, 60, 2, rad=10); save(sweep(im), "video_bg2_venues.png")
im, d = base()
pts = [(960, 260+i*120) for i in range(8)]
d.line(pts, fill=(60, 62, 68), width=10)
for x, y in pts: d.ellipse([x-26, y-26, x+26, y+26], fill=AMBER, outline=INK, width=4)
save(im, "video_bg3_cities.png")
im, d = base(); d.ellipse([960-260, 760-260, 960+260, 760+260], outline=AMBER, width=18)
d.line([960, 760, 960, 560], fill=INK, width=18); d.line([960, 760, 1110, 840], fill=AMBER, width=14)
d.ellipse([940, 740, 980, 780], fill=INK); save(im, "video_bg4_hours.png")
im, d = base(); d.polygon([(960, 470), (1110, 700), (960, 1020), (810, 700)], fill=AMBER)
d.ellipse([920, 620, 1000, 700], fill=BG); dots(d, 20, 5, col=(80, 82, 88), rad=9); save(im, "video_bg5_listed.png")
