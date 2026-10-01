"""Ajoute des legendes STYLE MINECRAFT sur les captures d'ecran.

Utilise la police authentique du jeu (assets/minecraft/textures/font/ascii.png,
extraite du client.jar), avec l'ombre portee d'un pixel comme le fait le jeu.

La largeur de chaque glyphe est MESUREE sur la feuille (boite englobante de l'encre)
et non supposee : la police Minecraft a des largeurs variables, une avance fixe
couperait les caracteres larges ou laisserait des trous.

Entrees  : dist/shader_raw/*.png (les captures brutes)
Sortie   : dist/shader_gallery/*.png (captures legendees, pretes a uploader)

Legendes : dist/shader_captions.json  { "fichier.png": "texte de la legende", ... }

Modes :
  caption  - legende en bas a gauche sur une plaque sombre translucide
  compare  - deux images cote a cote, etiquettees (ideal pour montrer l'avant/apres)

Usage:
  python scripts/shader_gallery_text.py --font <ascii.png> [--scale 4]
  python scripts/shader_gallery_text.py --compare "sans.png" "avec.png" "WITHOUT SHADERS" "VANILLA+ POTATO"
"""

import argparse
import json
import os

from PIL import Image, ImageDraw

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "dist", "shader_raw")
OUT = os.path.join(BASE, "dist", "shader_gallery")
CAPTIONS = os.path.join(BASE, "dist", "shader_captions.json")

GLYPH = 8          # cellule d'un glyphe dans la feuille
COLS = 16          # colonnes de la feuille
# La feuille est indexee par le CODE DU CARACTERE directement : col = c % 16,
# row = c // 16. AUCUN offset a 0x20. Verifie empiriquement sur l'ascii.png de
# 1.21.4 : cette convention donne 'I' de largeur 3 et les autres majuscules 5,
# alors que l'offset 0x20 produit des largeurs incoherentes ('A' de largeur 1).


class McFont:
    """Police Minecraft : feuille 16x16 de cellules 8x8, largeurs mesurees."""

    def __init__(self, path):
        sheet = Image.open(path).convert("RGBA")
        self.sheet = sheet
        self.glyph = {}
        for code in range(COLS * COLS):
            i = code
            box = ((i % COLS) * GLYPH, (i // COLS) * GLYPH,
                   (i % COLS) * GLYPH + GLYPH, (i // COLS) * GLYPH + GLYPH)
            g = sheet.crop(box)
            # avance = derniere colonne contenant de l'encre + 1 px d'interlettre
            alpha = g.getchannel("A")
            w = 0
            for x in range(GLYPH):
                if any(alpha.getpixel((x, y)) > 24 for y in range(GLYPH)):
                    w = x + 1
            self.glyph[code] = (g, w)

    def width(self, text, scale, tracking=1):
        total = 0
        for ch in text:
            g, w = self.glyph.get(ord(ch), self.glyph[ord("?")])
            total += (w + tracking) * scale
        return total

    def draw(self, img, text, x, y, scale, colour=(255, 255, 255), shadow=True):
        """Dessine le texte. L'ombre decalee d'un pixel est ce qui donne le look du jeu.

        On n'utilise QUE le canal alpha du glyphe comme masque : la couleur d'encre de
        la feuille n'a pas d'importance, seule sa forme compte."""
        passes = []
        if shadow:
            passes.append(((12, 12, 16, 220), scale, scale))
        passes.append((colour + (255,), 0, 0))

        for col, dx, dy in passes:
            cx = x + dx
            for ch in text:
                g, w = self.glyph.get(ord(ch), self.glyph[ord("?")])
                if w:
                    big = g.resize((GLYPH * scale, GLYPH * scale), Image.NEAREST)
                    tinted = Image.new("RGBA", big.size, col)
                    tinted.putalpha(big.getchannel("A"))
                    img.paste(tinted, (cx, y + dy), tinted)
                cx += (w + 1) * scale


def plate(img, box, alpha=140):
    """Plaque sombre translucide derriere le texte, pour rester lisible sur toute image."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rectangle(box, fill=(10, 11, 14, alpha))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def caption(src, text, font, scale, out_path):
    img = Image.open(src).convert("RGBA")
    pad = 18 * scale // 4
    w = font.width(text, scale)
    h = GLYPH * scale
    x, y = 40, img.height - h - 48
    img = plate(img, (x - pad, y - pad, x + w + pad, y + h + pad))
    font.draw(img, text, x, y, scale)
    img.convert("RGB").save(out_path)
    return out_path


def compare(left, right, label_l, label_r, font, scale, out_path):
    a = Image.open(left).convert("RGBA")
    b = Image.open(right).convert("RGBA")
    h = min(a.height, b.height)
    a = a.resize((int(a.width * h / a.height), h), Image.LANCZOS)
    b = b.resize((int(b.width * h / b.height), h), Image.LANCZOS)
    canvas = Image.new("RGBA", (a.width + b.width, h), (0, 0, 0, 255))
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width, 0))

    # trait de separation
    ImageDraw.Draw(canvas).line([(a.width, 0), (a.width, h)], fill=(255, 255, 255, 90), width=2)

    for img_x, txt in ((0, label_l), (a.width, label_r)):
        tw = font.width(txt, scale)
        x, y = img_x + 40, h - GLYPH * scale - 48
        canvas = plate(canvas, (x - 18 * scale // 4, y - 18 * scale // 4,
                                x + tw + 18 * scale // 4, y + GLYPH * scale + 18 * scale // 4))
        font.draw(canvas, txt, x, y, scale)
    canvas.convert("RGB").save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True, help="chemin vers ascii.png extrait du client.jar")
    ap.add_argument("--scale", type=int, default=4, help="agrandissement des glyphes")
    ap.add_argument("--compare", nargs=4, metavar=("GAUCHE", "DROITE", "TXT_GAUCHE", "TXT_DROITE"))
    args = ap.parse_args()

    font = McFont(args.font)
    os.makedirs(OUT, exist_ok=True)

    if args.compare:
        out = os.path.join(OUT, "comparison.png")
        compare(args.compare[0], args.compare[1], args.compare[2], args.compare[3],
                font, args.scale, out)
        print("ecrit :", out)
        return

    caps = {}
    if os.path.isfile(CAPTIONS):
        caps = json.load(open(CAPTIONS, encoding="utf-8"))

    files = sorted(f for f in os.listdir(RAW) if f.lower().endswith((".png", ".jpg", ".jpeg"))) \
        if os.path.isdir(RAW) else []
    if not files:
        print(f"aucune capture dans {RAW}")
        return

    for f in files:
        text = caps.get(f, os.path.splitext(f)[0].upper())
        out = os.path.join(OUT, os.path.splitext(f)[0] + ".png")
        caption(os.path.join(RAW, f), text, font, args.scale, out)
        print(f"  {f}  ->  {os.path.basename(out)}   「{text}」")

    print(f"\n{len(files)} legende(s) ecrite(s) dans {OUT}")


if __name__ == "__main__":
    main()
