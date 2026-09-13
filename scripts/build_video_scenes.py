#!/usr/bin/env python3
"""Build 4 vertical 1080x1920 scenes for the Clear Pumpkin demo short."""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

BASE = os.path.expanduser("~/fliflight-mods")
VANILLA = f"{BASE}/packs/pvp-essentials/gallery_src/vanilla"
OUT = f"{BASE}/dist/video/scenes"
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920
FONT_BIG = r"C:\Windows\Fonts\impact.ttf"
FONT_SUB = r"C:\Windows\Fonts\arialbd.ttf"

def tex(name, scale):
    im = Image.open(f"{VANILLA}/{name}.png").convert("RGBA")
    return im.resize((im.width*scale, im.height*scale), Image.NEAREST)

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def vgradient(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / H
        r = int(top[0] + (bottom[0]-top[0])*t)
        g = int(top[1] + (bottom[1]-top[1])*t)
        b = int(top[2] + (bottom[2]-top[2])*t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return img

def glow(img, radius=40):
    """Add a soft glow behind a sprite: paste sprite over blurred bright copy."""
    bright = ImageEnhance.Brightness(img).enhance(1.6)
    blurred = bright.filter(ImageFilter.GaussianBlur(radius))
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # center
    x = (W - img.width)//2
    y = (H - img.height)//2
    canvas.alpha_composite(blurred, (x-30, y-30))
    return canvas

def paste_center(base_rgba, sprite, cx, cy, scale=1.0):
    if scale != 1.0:
        sprite = sprite.resize((int(sprite.width*scale), int(sprite.height*scale)), Image.NEAREST)
    x = int(cx - sprite.width/2)
    y = int(cy - sprite.height/2)
    base_rgba.alpha_composite(sprite, (x, y))
    return base_rgba

def draw_text_block(draw, lines, center_x, top_y, font_path, size, fill=(255,255,255), stroke=(0,0,0), stroke_w=6, line_gap=None):
    """Draw stacked centered text lines with stroke, returns bottom y."""
    font = load_font(font_path, size)
    if line_gap is None:
        line_gap = int(size*0.12)
    y = top_y
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font, stroke_width=stroke_w)
        tw = bbox[2]-bbox[0]
        draw.text((center_x - tw/2, y), line, font=font, fill=fill,
                  stroke_width=stroke_w, stroke_fill=stroke)
        y += size + line_gap
    return y

def scene1():
    """Hook: big carved pumpkin staring, dark cave vibe."""
    bg = vgradient((18, 12, 8), (6, 4, 2))
    base = bg.convert("RGBA")
    pumpkin = tex("carved_pumpkin", 36)  # 576px block
    # glow behind
    glow_im = ImageEnhance.Brightness(pumpkin).enhance(1.3).filter(ImageFilter.GaussianBlur(50))
    base.alpha_composite(glow_im, ((W-576)//2 - 40, 600-40))
    base.alpha_composite(pumpkin, ((W-576)//2, 600))
    # subtle floating shadow ellipse
    sh = Image.new("RGBA", (700, 120), (0,0,0,0))
    d = ImageDraw.Draw(sh)
    d.ellipse((0, 0, 700, 120), fill=(0,0,0,120))
    base.alpha_composite(sh, ((W-700)//2, 1300))
    # vignette: radial mask computed per-pixel (center=255 -> corners=0), upscaled
    small = Image.new("L", (128, 128), 0)
    spx = small.load()
    cx = cy = 63.5
    maxd = (cx**2 + cy**2) ** 0.5
    for yy in range(128):
        for xx in range(128):
            d = ((xx-cx)**2 + (yy-cy)**2) ** 0.5 / maxd
            spx[xx, yy] = int(255 * max(0.0, 1.0 - d) ** 1.6)
    vig = small.resize((W, H), Image.LANCZOS)
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base = Image.composite(base, dark, vig)  # center keeps base, corners -> dark
    draw = ImageDraw.Draw(base)
    draw_text_block(draw, ["OK. J'AI UN", "PROBLÈME."], W//2, 150, FONT_BIG, 130, (255, 80, 40), (0,0,0), 10)
    base.convert("RGB").save(f"{OUT}/scene1.png", quality=95)

def scene2():
    """Blur vs clear split — the pain point."""
    bg = vgradient((30, 22, 14), (10, 7, 4))
    base = bg.convert("RGBA")
    pumpkin = tex("carved_pumpkin", 26)  # 416px
    # LEFT: blurred
    bl = pumpkin.filter(ImageFilter.GaussianBlur(14))
    # darkened + slightly desaturated
    bl = ImageEnhance.Brightness(bl).enhance(0.7)
    # RIGHT: clear with glow
    cl = pumpkin
    glow_im = ImageEnhance.Brightness(cl).enhance(1.5).filter(ImageFilter.GaussianBlur(30))
    y_center = 900
    base.alpha_composite(bl, (60, y_center - bl.height//2))
    gx = W - 60 - cl.width
    base.alpha_composite(glow_im, (gx-30, y_center - cl.height//2 - 30))
    base.alpha_composite(cl, (gx, y_center - cl.height//2))
    # labels
    draw = ImageDraw.Draw(base)
    f = load_font(FONT_SUB, 54)
    draw.text((60, y_center + 260), "AVANT : FLOU", font=f, fill=(200, 200, 200), stroke_width=4, stroke_fill=(0,0,0))
    tw = draw.textbbox((0,0), "APRÈS : NET", font=f, stroke_width=4)[2]
    draw.text((W-60-tw, y_center + 260), "APRÈS : NET", font=f, fill=(120, 255, 120), stroke_width=4, stroke_fill=(0,0,0))
    # arrow
    draw.text((W//2-40, y_center - 30), "➜", font=load_font(FONT_BIG, 90), fill=(255,255,255), stroke_width=4, stroke_fill=(0,0,0))
    draw_text_block(draw, ["LE FLOU QUAND TU", "PORTES UNE CITROUILLE"], W//2, 180, FONT_BIG, 105, (255,255,255), (0,0,0), 8)
    draw_text_block(draw, ["... c'est invivable."], W//2, 1620, FONT_SUB, 64, (255, 200, 100), (0,0,0), 6)
    base.convert("RGB").save(f"{OUT}/scene2.png", quality=95)

def scene3():
    """Pack applied: clear pumpkin + silly 'I see everything' moment."""
    bg = vgradient((40, 55, 30), (12, 18, 8))
    base = bg.convert("RGBA")
    pumpkin = tex("carved_pumpkin", 30)
    glow_im = ImageEnhance.Brightness(pumpkin).enhance(1.5).filter(ImageFilter.GaussianBlur(45))
    base.alpha_composite(glow_im, ((W-480)//2 - 30, 560-30))
    base.alpha_composite(pumpkin, ((W-480)//2, 560))
    # sunglasses gag: simple dark bar over eyes area of pumpkin
    sg = Image.new("RGBA", (520, 60), (0,0,0,0))
    dsg = ImageDraw.Draw(sg)
    dsg.rectangle((0, 0, 230, 60), fill=(10,10,10,255))
    dsg.rectangle((290, 0, 520, 60), fill=(10,10,10,255))
    dsg.rectangle((220, 20, 300, 45), fill=(10,10,10,255))
    base.alpha_composite(sg, ((W-520)//2, 800))
    draw = ImageDraw.Draw(base)
    draw_text_block(draw, ["MON PACK L'ENLÈVE."], W//2, 170, FONT_BIG, 120, (120, 255, 120), (0,0,0), 10)
    draw_text_block(draw, ["Je vois TOUT."], W//2, 1300, FONT_BIG, 150, (255, 255, 255), (0,0,0), 10)
    draw_text_block(draw, ["Et maintenant... je fais n'importe quoi 😎"], W//2, 1620, FONT_SUB, 58, (255, 255, 120), (0,0,0), 6)
    base.convert("RGB").save(f"{OUT}/scene3.png", quality=95)

def scene4():
    """CTA: pack icon + download info."""
    bg = vgradient((10, 10, 14), (4, 4, 6))
    base = bg.convert("RGBA")
    # grid floor feel
    draw = ImageDraw.Draw(base)
    icon = Image.open(f"{BASE}/packs/fliflight-clear-pumpkin/icon.png").convert("RGBA")
    icon = icon.resize((320, 320), Image.NEAREST)
    glow_im = ImageEnhance.Brightness(icon).enhance(1.5).filter(ImageFilter.GaussianBlur(40))
    base.alpha_composite(glow_im, ((W-320)//2 - 25, 500-25))
    base.alpha_composite(icon, ((W-320)//2, 500))
    # barrier motif small at top corners to reference 'fix'
    draw_text_block(draw, ["CLEAR PUMPKIN"], W//2, 180, FONT_BIG, 140, (255, 170, 40), (0,0,0), 10)
    draw_text_block(draw, ["Fini le flou de citrouille."], W//2, 920, FONT_SUB, 62, (255,255,255), (0,0,0), 6)
    # download pill
    pill = Image.new("RGBA", (W-160, 150), (0,0,0,0))
    dp = ImageDraw.Draw(pill)
    dp.rounded_rectangle((0, 0, W-160, 150), radius=40, fill=(46, 204, 64, 255))
    base.alpha_composite(pill, (80, 1240))
    draw = ImageDraw.Draw(base)
    ftxt = load_font(FONT_BIG, 76)
    line = "GRATUIT SUR CURSEFORGE"
    tw = draw.textbbox((0,0), line, font=ftxt)[2]
    draw.text((W//2 - tw/2, 1240+35), line, font=ftxt, fill=(255,255,255))
    draw_text_block(draw, ["Lien en bio ⬇"], W//2, 1480, FONT_SUB, 72, (255, 255, 255), (0,0,0), 6)
    base.convert("RGB").save(f"{OUT}/scene4.png", quality=95)

scene1()
scene2()
scene3()
scene4()
for i in range(1, 5):
    print(f"scene{i}.png", os.path.getsize(f"{OUT}/scene{i}.png")//1024, "KB")
print("OK")
