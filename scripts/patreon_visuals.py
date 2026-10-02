"""Genere les visuels Patreon de FliflightMC (banniere + avatar).
Typographique, local, aucun rendu Minecraft simule.

Piege corrige (v1 -> v2) : `font.getbbox()` renvoie la hauteur D'ENCRE (hauteur de
capitale), pas la hauteur de ligne -> le filet sous le titre tombait dans les lettres.
Ici on utilise `getmetrics()` (ascent + descent) pour l'interlignage et le placement.
Autres correctifs v2 : bloc texte remonte et centre, largeur de texte plafonnee pour
ne pas empieter sur le crosshair, bras longs du crosshair raccourcis, mot-symbole de
l'avatar bride a la corde du cercle (assert de controle).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.expanduser("~/fliflight-mods/dist/patreon")
os.makedirs(OUT, exist_ok=True)

CYAN = (34, 211, 238)
PURPLE = (168, 85, 247)
DARK_A = (7, 9, 18)
DARK_B = (21, 12, 46)
WHITE = (240, 244, 252)
GREY = (176, 190, 208)
FONT_BLACK = "C:/Windows/Fonts/ariblk.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"


def diag_gradient(w, h, c1, c2, step=6):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(0, w, step):
            t = max(0.0, min(1.0, x / w * 0.55 + y / h * 0.45))
            col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
            for dx in range(step):
                if x + dx < w:
                    px[x + dx, y] = col
    return img


def lin_grad(w, c1, c2):
    g = Image.new("RGB", (max(2, w), 2), (0, 0, 0))
    px = g.load()
    for x in range(g.size[0]):
        t = x / max(1, g.size[0] - 1)
        col = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        px[x, 0] = col
        px[x, 1] = col
    return g


def tw(text, font, tracking=0.0):
    """Largeur d'avance du texte, espacement de lettres inclus."""
    return font.getlength(text) + tracking * (len(text) - 1)


def fit(text, path, max_w, start, tracking=0.0, min_size=8):
    size = start
    while size > min_size:
        f = ImageFont.truetype(path, size)
        if tw(text, f, tracking) <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(path, min_size)


def line_h(font):
    a, d = font.getmetrics()
    return a + d


def text_mask(size, text, font, tracking=0.0):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    x = 0.0
    for ch in text:
        d.text((x, 0), ch, font=font, fill=255)
        x += font.getlength(ch) + tracking
    return m


def paste_text(dst, xy, text, font, tracking=0.0, color=None, grad=None, shadow=4):
    """Ecrit le texte (couleur pleine ou degrade horizontal) + ombre portee.

    Le masque est dessine a l'ORIGINE et la couleur aussi : c'est le
    `alpha_composite(..., dest=xy)` final qui positionne le tout. Coller la couleur
    en (x, y) pendant que le masque reste en (0, 0) produit du texte noir en haut a
    gauche (RGB 0 de la zone vide) — bug corrige en v3.
    """
    x, y = int(xy[0]), int(xy[1])
    W, H = dst.size
    mask = text_mask(dst.size, text, font, tracking)
    if shadow:
        sh = Image.new("RGBA", dst.size, (0, 0, 0, 0))
        sh.paste((0, 0, 0, 185), (0, 0, W, H), mask)
        dst.alpha_composite(sh, (x + shadow, y + shadow))
    if grad is not None:
        gw = max(2, int(tw(text, font, tracking)))
        tile = Image.new("RGBA", dst.size, (0, 0, 0, 0))
        tile.paste(grad.resize((gw, H), Image.BILINEAR).convert("RGBA"), (0, 0))
    else:
        # un tuple de couleur nu serait lu comme une region par PIL -> image pleine
        tile = Image.new("RGBA", dst.size, tuple(color) + (255,))
    tile.putalpha(mask)
    dst.alpha_composite(tile, (x, y))


def glow(layer, radius=20, gain=1.0):
    halo = layer.filter(ImageFilter.GaussianBlur(radius))
    if gain != 1.0:
        halo.putalpha(halo.split()[3].point(lambda v: min(255, int(v * gain))))
    return halo


def crosshair(draw, cx, cy, arm, gap, w, fill, dot=True):
    """Crosshair a 4 branches symetriques, style PvP."""
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        draw.line([cx + dx * gap, cy + dy * gap,
                   cx + dx * (gap + arm), cy + dy * (gap + arm)],
                  fill=fill, width=w)
    if dot:
        r = max(1, w // 2 + 1)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


# ---------------------------------------------------------------- BANNIERE
def make_cover(w, h, path):
    S = w / 1600.0
    ref = lambda v: int(round(v * S))
    cover = diag_gradient(w, h, DARK_A, DARK_B).convert("RGBA")

    grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    for i in range(-h, w, ref(46)):
        gd.line([(i, h), (i + h, 0)], fill=(255, 255, 255, 9), width=max(1, ref(1)))
    cover = Image.alpha_composite(cover, grid)

    M = ref(30)                                   # marge interieure
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rectangle([M, M, w - M, h - M],
                                    outline=CYAN + (46,), width=max(2, ref(2)))
    cover = Image.alpha_composite(cover, frame)

    # decoration a droite : crosshair (produit phare), entierement dans le cadre
    dcx, dcy = w - ref(200), int(h * 0.50)
    rr = ref(104)
    deco = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(deco)
    crosshair(dd, dcx, dcy, ref(74), ref(30), max(3, ref(8)), CYAN + (235,))
    dd.ellipse([dcx - rr, dcy - rr, dcx + rr, dcy + rr],
               outline=PURPLE + (120,), width=max(2, ref(3)))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dd.line([dcx + dx * ref(116), dcy + dy * ref(116),
                 dcx + dx * ref(154), dcy + dy * ref(154)],
                fill=PURPLE + (170,), width=max(2, ref(4)))
    cover = Image.alpha_composite(cover, glow(deco, radius=ref(24), gain=0.85))
    cover = Image.alpha_composite(cover, deco)

    # bloc texte : centre verticalement, largeur plafonnee, bas-gauche libre (avatar)
    x0 = ref(96)
    MAXW = ref(740)
    tr = ref(7)
    title = "FLIFLIGHT MC"
    tag = "MINECRAFT PVP  \u2022  PACKS, MODS & SHADERS"
    sub = "Acc\u00e8s anticip\u00e9  \u00b7  Packs exclusifs  \u00b7  Soutien direct"
    f_title = fit(title, FONT_BLACK, MAXW, ref(150), tr)
    f_tag = fit(tag, FONT_BOLD, MAXW, ref(50))
    f_sub = fit(sub, FONT_BOLD, MAXW, ref(40))

    lh1, lh2, lh3 = line_h(f_title), line_h(f_tag), line_h(f_sub)
    gap1, gap2 = ref(16), ref(18)
    y0 = int((h - (lh1 + gap1 + lh2 + gap2 + lh3)) / 2)

    paste_text(cover, (x0, y0), title, f_title, tr,
               grad=lin_grad(int(tw(title, f_title, tr)), CYAN, PURPLE), shadow=ref(5))
    y1 = y0 + lh1 + gap1
    paste_text(cover, (x0, y1), tag, f_tag, 0, color=WHITE, shadow=ref(3))
    y2 = y1 + lh2 + gap2
    paste_text(cover, (x0, y2), sub, f_sub, 0, color=GREY, shadow=ref(3))

    # filet cyan place SOUS la ligne de base reelle du titre
    yr = y0 + lh1 + ref(6)
    ru = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(ru).rectangle([x0, yr, x0 + ref(200), yr + max(3, ref(6))],
                                 fill=CYAN + (255,))
    cover = Image.alpha_composite(cover, glow(ru, radius=ref(10), gain=0.7))
    cover = Image.alpha_composite(cover, ru)

    assert yr + ref(8) <= y1, "filet qui chevauche le sous-titre"
    assert x0 + max(tw(title, f_title, tr), tw(tag, f_tag), tw(sub, f_sub)) < dcx - rr, \
        "texte qui empiète sur le crosshair"

    cover.convert("RGB").save(path, "PNG")
    return path


# ------------------------------------------------------------------ AVATAR
def make_avatar(size, path):
    S = size / 512.0
    ref = lambda v: int(round(v * S))
    av = diag_gradient(size, size, DARK_A, DARK_B).convert("RGBA")

    halo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([size * 0.12, size * 0.12, size * 0.88, size * 0.88],
                                 fill=(30, 92, 165, 95))
    av = Image.alpha_composite(av, halo.filter(ImageFilter.GaussianBlur(64 * S)))

    ring_r = int(size * 0.36)                     # rayon du cercle neon
    c = size // 2
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([c - ring_r, c - ring_r, c + ring_r, c + ring_r],
                                 outline=CYAN + (175,), width=max(3, ref(7)))
    av = Image.alpha_composite(av, glow(ring, radius=ref(15), gain=0.8))

    # crosshair centre dans la moitie haute
    cx, cy = c, int(size * 0.340)
    ch = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cd = ImageDraw.Draw(ch)
    crosshair(cd, cx, cy, ref(66), ref(23), max(5, ref(11)), CYAN + (255,))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cd.line([cx + dx * ref(95), cy + dy * ref(95),
                 cx + dx * ref(123), cy + dy * ref(123)],
                fill=PURPLE + (200,), width=max(3, ref(5)))
    av = Image.alpha_composite(av, glow(ch, radius=ref(18), gain=0.95))
    av = Image.alpha_composite(av, ch)

    # mot-symbole : police ajustee a la corde du cercle a la hauteur du mot
    def half_at(yy):
        dyc = abs(yy - c)
        return int(max(0, ring_r * ring_r - dyc * dyc) ** 0.5)

    word = "FLIFLIGHT"
    ty = int(size * 0.605)
    f = fit(word, FONT_BLACK, ref(240), ref(46))
    for _ in range(40):
        gw, lh = int(tw(word, f)), line_h(f)
        avail = 2 * min(half_at(ty), half_at(ty + lh)) - ref(16)
        if gw <= avail:
            break
        f = ImageFont.truetype(FONT_BLACK, max(9, f.size - 1))
    gw, lh = int(tw(word, f)), line_h(f)
    gx = c - gw // 2
    paste_text(av, (gx, ty), word, f, 0, grad=lin_grad(gw, WHITE, CYAN), shadow=ref(4))

    # controles : tous les coins du bloc texte dans le cercle, pas de collision
    ray = ring_r - ref(6)
    for px, py in ((gx, ty), (gx + gw, ty), (gx, ty + lh), (gx + gw, ty + lh)):
        d = ((px - c) ** 2 + (py - c) ** 2) ** 0.5
        assert d <= ray, f"coin du mot-symbole hors cercle ({d:.0f} > {ray})"
    assert cy + ref(123) < ty, "bras bas du crosshair qui touche le mot-symbole"
    assert f.size >= ref(30), f"mot-symbole trop petit ({f.size}px)"

    av.convert("RGB").save(path, "PNG")
    return path


print(make_cover(3200, 800, f"{OUT}/patreon-cover-3200x800.png"))
print(make_cover(1600, 400, f"{OUT}/patreon-cover-1600x400.png"))
print(make_avatar(512, f"{OUT}/patreon-avatar-512x512.png"))
for f in sorted(os.listdir(OUT)):
    p = os.path.join(OUT, f)
    print(f, Image.open(p).size, os.path.getsize(p), "o")
