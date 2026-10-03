#!/usr/bin/env python3
"""Build the Fliflight Xray packs — one Java, one Bedrock.

Designed after reading two third-party packs the user supplied as references. No file is copied
from either; the techniques were learned and reimplemented independently.

WHY THE FIRST JAVA BUILD FAILED

  1. Blanking block TEXTURES does not work. An opaque block renders with the "solid" material,
     which ignores alpha and paints the raw RGB, so transparent stone shows up as BLACK stone.
     A working Xray pack on this machine ships 484 blockstates, 823 models and zero block
     textures. The effect is geometry: a 0.5-unit shell on each of the six faces, every face
     carrying "cullface" so it is only drawn against a non-opaque neighbour.

  2. A hardcoded block list always leaves gaps. The user's screenshots showed andesite, tuff,
     bedrock and sculk still fully opaque. The list is now DERIVED from the vanilla jar: every
     model whose parent chain reaches a cube family is a full block, and every full block is
     covered except the ores.

  3. The shell declared no "particle" texture, so breaking a block sprayed magenta-and-black
     missing-texture particles. Each override now supplies an explicit particle texture.

BEDROCK is a different mechanism entirely: blocks.json declares a block's SHAPE as "invisible",
with no textures and no models.

Run:  python scripts/build_xray.py
"""
import io
import json
import os
import re
import shutil
import uuid
import zipfile

from PIL import Image, ImageDraw, ImageFilter

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
BUILD = os.path.join(BASE, "build")
JAR = os.path.join(BUILD, "client-1.21.4.jar")
TEX = "assets/minecraft/textures/"

JAVA_SLUG = "fliflight-xray-java"
BED_SLUG = "fliflight-xray-bedrock"
NOM = "Xray - See Through Terrain"
ESPACE = "fliflight_xray"

# Familles de modeles qui decrivent un bloc plein (un cube). Tout modele qui descend de l'une
# d'elles est un bloc a rendre transparent.
FAMILLES_CUBE = re.compile(r"^(cube|orientable)")
# Modeles abstraits : ce sont des gabarits, pas des blocs. Il est CRITIQUE de les exclure :
# ecrire un assets/minecraft/models/block/cube_all.json dans le pack ECRASERAIT le gabarit
# vanilla, dont heritent tous les minerais. Les minerais deviendraient transparents — l'inverse
# exact du but. Le premier build ne les avait pas ecrits, mais uniquement par accident (leur
# resolution de texture echouait) ; des que le repli de texture a ete elargi, ils passaient.
GABARITS = re.compile(r"^(template_|cube(_|$)|orientable(_|$))")
# Minerais : a laisser pleinement visibles. Le motif exige un separateur, sinon "mirrored"
# (mirr-ore-d) serait pris pour un minerai et des blocs entiers seraient ecartes a tort.
MINERAIS = re.compile(r"(^|_)ore($|_)|(^|_)raw_")

# Textures de blocs ecartees a la main (blocs techniques sans interet a traverser).
DENYLIST = {"air", "barrier", "light", "structure_void", "moving_piston", "piston_head",
            "nether_portal", "end_portal", "end_gateway", "bubble_column", "water", "lava",
            "fire", "frosted_ice"}

# Blocs pleins dont les textures ne se resolvent pas en remontant la chaine : mappees a la main.
SECOURS = {
    "pumpkin": {"all": "block/pumpkin_side", "top": "block/pumpkin_top"},
    "carved_pumpkin": {"all": "block/pumpkin_side", "top": "block/pumpkin_top",
                       "front": "block/carved_pumpkin"},
    "jack_o_lantern": {"all": "block/pumpkin_side", "top": "block/pumpkin_top",
                       "front": "block/jack_o_lantern"},
}

# Bedrock : meme intention, identifiants propres a cette edition.
BEDROCK_BLOCS = [
    "stone", "granite", "diorite", "andesite", "deepslate", "tuff", "calcite",
    "dripstone_block", "netherrack", "basalt", "blackstone", "end_stone", "obsidian",
    "dirt", "coarse_dirt", "rooted_dirt", "grass_block", "podzol", "mycelium",
    "gravel", "clay", "sand", "red_sand", "sandstone", "red_sandstone",
    "cobblestone", "mossy_cobblestone", "stone_bricks", "mud", "packed_mud",
    "soul_sand", "soul_soil", "moss_block", "snow_layer", "powder_snow",
    "oak_leaves", "spruce_leaves", "birch_leaves", "jungle_leaves", "acacia_leaves",
    "dark_oak_leaves", "mangrove_leaves", "cherry_leaves", "azalea_leaves",
    "flowering_azalea_leaves", "hardened_clay", "crimson_nylium", "warped_nylium",
    "crimson_roots", "warped_roots", "deadbush", "glow_lichen", "hanging_roots",
    "mushroom_stem", "muddy_mangrove_roots", "reeds", "sculk", "bedrock",
]

# Overlays qui masquent la vue. Ce sont de vraies textures a canal alpha : les vider fonctionne
# (contrairement aux textures de blocs, voir l'en-tete).
OVERLAYS = ["misc/pumpkinblur", "misc/underwater", "misc/vignette", "misc/powder_snow_outline"]

_cube_cache = {}


def modeles_vanilla(z):
    out = {}
    for n in z.namelist():
        if n.startswith("assets/minecraft/models/block/") and n.endswith(".json"):
            try:
                out[n.split("/")[-1][:-5]] = json.loads(z.read(n).decode("utf-8", "replace"))
            except Exception:
                pass
    return out


def est_bloc_plein(nom, mods, prof=0):
    """Vrai si le modele descend d'une famille cube — donc s'il occupe un cube entier."""
    if nom in _cube_cache:
        return _cube_cache[nom]
    _cube_cache[nom] = None
    if prof > 8:
        return None
    p = (mods.get(nom) or {}).get("parent")
    if not p:
        return None
    court = p.split("/")[-1]
    if p.startswith("minecraft:"):
        court = p.split(":")[1].split("/")[-1]
    r = court if FAMILLES_CUBE.match(court) else est_bloc_plein(court, mods, prof + 1)
    _cube_cache[nom] = r
    return r


def textures_resolues(nom, mods):
    """Remonte la chaine de parents, fusionne les textures, puis resout les references '#'."""
    brut, cur, prof = {}, nom, 0
    while cur and prof < 12:
        m = mods.get(cur) or {}
        for k, v in (m.get("textures") or {}).items():
            brut.setdefault(k, v)
        cur = m.get("parent")
        if cur and cur.startswith("block/"):
            cur = cur.split("/", 1)[1]
        prof += 1
    resolu = {}
    for k, v in brut.items():
        for _ in range(6):
            if isinstance(v, str) and v.startswith("#"):
                v = brut.get(v[1:], v)
            else:
                break
        if isinstance(v, str) and not v.startswith("#"):
            resolu[k] = v if ":" in v else "minecraft:" + v
    return resolu


def faces_pour(tex):
    """Traduit un jeu de textures vanilla (all / side / end / top / front) vers les 6 faces
    de la coque, plus la texture de particule. C'est ce qui manquait : sans 'particle' explicite,
    casser un bloc crachait des particules magenta de texture manquante."""
    def pick(*noms):
        for n in noms:
            if n in tex:
                return tex[n]
        return None

    tout = pick("all", "side", "texture", "top", "end", "up", "down",
                "north", "south", "east", "west", "pattern")
    if not tout:
        # Dernier recours : n'importe quelle texture resolue. Mieux vaut un bloc transparent avec
        # une texture approchante qu'un bloc qui reste opaque et cache le terrain — c'est
        # exactement le defaut que l'utilisateur a signale sur l'andesite, le tuf et le bedrock.
        tout = next((v for v in tex.values() if isinstance(v, str) and ":" in v), None)
    if not tout:
        return None
    f = {
        "down": pick("down", "bottom", "end", "all") or tout,
        "up": pick("up", "top", "end", "all") or tout,
        "north": pick("north", "front", "side", "all") or tout,
        "south": pick("south", "side", "all") or tout,
        "east": pick("east", "side", "all") or tout,
        "west": pick("west", "side", "all") or tout,
    }
    f["particle"] = pick("particle") or f["up"]
    return f


def coque():
    """Le coeur du pack : six dalles de 0,5 unite, une par face, chacune avec 'cullface'.

    Une face portant 'cullface' n'est dessinee que si le bloc voisin de ce cote n'est pas opaque.
    Entre deux blocs de pierre rien n'est donc dessine, et le terrain se reduit a un liseré.
    Chaque face porte AUSSI sa texture propre (#up, #side...) et non une texture unique : sans
    ca, les blocs a plusieurs textures (herbe, grès, deepslate) s'affichent faux.
    """
    d, e = 0.5, 16.0
    plans = [
        ([0, 0, 0], [e, e, d], {"east": [e - d, 0, e, e], "west": [0, 0, d, e],
                                "up": [0, e - d, e, e], "down": [0, 0, e, d]}),
        ([0, 0, e - d], [e, e, e], {"east": [0, 0, d, e], "west": [e - d, 0, e, e],
                                    "up": [0, 0, e, d], "down": [0, e - d, e, e]}),
        ([0, e - d, 0], [e, e, e], {"north": [0, 0, e, d], "south": [0, 0, e, d],
                                    "east": [0, 0, e, d], "west": [0, 0, e, d]}),
        ([0, 0, 0], [e, d, e], {"north": [0, e - d, e, e], "south": [0, e - d, e, e],
                                "east": [0, e - d, e, e], "west": [0, e - d, e, e]}),
        ([0, 0, 0], [d, e, e], {"north": [d, 0, e, e], "south": [0, 0, e - d, e],
                                "up": [d, 0, e, e], "down": [d, 0, e, e]}),
        ([e - d, 0, 0], [e, e, e], {"north": [0, 0, e - d, e], "south": [d, 0, e, e],
                                    "up": [0, 0, e - d, e], "down": [0, 0, e - d, e]}),
    ]
    return {
        "parent": "minecraft:block/block",
        "ambientocclusion": False,
        "textures": {"particle": "#particle"},
        "elements": [
            {"from": f, "to": t, "light_emission": 15,
             "faces": {c: {"uv": uv, "texture": "#" + c, "cullface": c} for c, uv in faces.items()}}
            for f, t, faces in plans
        ],
    }


def vanilla(rel):
    with zipfile.ZipFile(JAR) as z:
        return z.read(TEX + rel + ".png")


def icone(size, minerai="block/diamond_ore"):
    """Style maison : fond plat sombre, bloc au premier plan, halo cyan serre."""
    img = Image.new("RGB", (size, size), (13, 14, 18))
    art = Image.open(io.BytesIO(vanilla(minerai))).convert("RGBA")
    bbox = art.getbbox()
    if bbox:
        art = art.crop(bbox)
    # Echelle ENTIERE, obligatoire : l'icone s'affiche a 32 px dans la liste des packs, donc le
    # bloc doit y mesurer 16 px (1 texel = 1 pixel) ou 32 px (2 px par texel). Un facteur comme
    # 0,55 donne 17 texels et un reechantillonnage non entier : net en 512, flou en jeu.
    ech = max(1, size // 32)
    iw = ih = art.size[0] * ech
    off = ((size - iw) // 2, (size - ih) // 2)

    glow = Image.new("L", (size, size), 0)
    pad = max(3, int(max(iw, ih) * 0.34))
    ImageDraw.Draw(glow).rounded_rectangle(
        [off[0]-pad, off[1]-pad, off[0]+iw+pad, off[1]+ih+pad],
        radius=int(max(iw, ih)*0.34), fill=95)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(4, max(iw, ih)//6)))
    cyan = Image.new("RGB", (size, size), (90, 220, 235))
    img = Image.blend(img, Image.composite(cyan, img, glow), 0.42)

    art = art.resize((iw, ih), Image.NEAREST)
    u = max(1, size // 32)
    d = ImageDraw.Draw(img)
    x0, y0 = off[0] - u, off[1] - u
    x1, y1 = off[0] + iw - 1 + u, off[1] + ih - 1 + u
    d.rectangle([x0 + u, y0 + u, x1 + u, y1 + u], fill=(5, 6, 9))
    d.rectangle([x0, y0, x1, y1], fill=(74, 84, 99))
    d.line([x0, y0, x1, y0], fill=(168, 180, 194), width=u)
    d.line([x0, y0, x0, y1], fill=(168, 180, 194), width=u)
    img.paste(art, off, art)
    return img


def build_java():
    print("\n--- JAVA ---")
    st = os.path.join(BUILD, JAVA_SLUG)
    if os.path.isdir(st):
        shutil.rmtree(st)
    racine = os.path.join(st, "assets", "minecraft")
    os.makedirs(os.path.join(racine, "models", "block", ESPACE), exist_ok=True)

    with zipfile.ZipFile(JAR) as z:
        mods = modeles_vanilla(z)
        tex_dispo = {n[len(TEX):-4] for n in z.namelist()
                     if n.startswith(TEX) and n.endswith(".png")}

    with open(os.path.join(racine, "models", "block", ESPACE, "shell.json"), "w", encoding="utf-8") as f:
        json.dump(coque(), f, indent=1)
    print(f"    {len(mods)} modeles lus dans le jar")

    ecrits, sans_tex, ecartes = [], [], []
    for nom in sorted(mods):
        if GABARITS.match(nom) or MINERAIS.search(nom) or nom in DENYLIST:
            ecartes.append(nom)
            continue
        if not est_bloc_plein(nom, mods):
            continue
        tex = textures_resolues(nom, mods)
        if nom in SECOURS:
            tex.update({k: ("minecraft:" + v if ":" not in v else v)
                        for k, v in SECOURS[nom].items()})
        faces = faces_pour(tex)
        if not faces:
            sans_tex.append(nom)
            continue
        # une texture qui n'existe pas dans le jeu laisserait un damier : on ecarte le bloc
        if any(t.split(":", 1)[1] not in tex_dispo for t in faces.values()):
            sans_tex.append(nom)
            continue
        with open(os.path.join(racine, "models", "block", nom + ".json"), "w", encoding="utf-8") as f:
            json.dump({"parent": f"minecraft:block/{ESPACE}/shell", "textures": faces}, f, indent=1)
        ecrits.append(nom)

    print(f"    {len(ecrits)} blocs pleins rendus transparents (dont feuillages)")
    print(f"    ecartes : {len(ecartes)} (minerais, gabarits, blocs techniques)")
    if sans_tex:
        print(f"    ignores faute de texture resolue : {len(sans_tex)} -> {sorted(sans_tex)[:10]}")

    for rel in OVERLAYS:
        try:
            im = Image.open(io.BytesIO(vanilla(rel))).convert("RGBA")
        except KeyError:
            continue
        im.putalpha(0)
        p = os.path.join(racine, "textures", rel + ".png")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)
    print("    overlays neutralises (pumpkinblur, underwater, vignette)")

    with open(os.path.join(st, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": 46,
                            "description": f"{NOM} — the rock around you becomes a faint lattice",
                            "supported_formats": {"min_inclusive": 46, "max_inclusive": 99}}},
                  f, indent=2, ensure_ascii=False)

    icone(128).save(os.path.join(st, "pack.png"))
    out = os.path.join(PACKS, JAVA_SLUG)
    os.makedirs(os.path.join(out, "files"), exist_ok=True)
    zn = f"{JAVA_SLUG}-1.0.0-resourcepack-1.21.4.zip"
    zp = os.path.join(out, "files", zn)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, names in os.walk(st):
            for n in names:
                full = os.path.join(root, n)
                z.write(full, os.path.relpath(full, st))
    shutil.copy(os.path.join(st, "pack.png"), os.path.join(out, "pack.png"))
    icone(512).save(os.path.join(out, "icon.png"))
    print(f"    + files/{zn}  ({os.path.getsize(zp)} octets)")
    return zp, ecrits


def build_bedrock():
    print("\n--- BEDROCK ---")
    st = os.path.join(BUILD, BED_SLUG)
    if os.path.isdir(st):
        shutil.rmtree(st)
    os.makedirs(st, exist_ok=True)
    with open(os.path.join(st, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "format_version": 2,
            "header": {"name": f"§b{NOM}", "description": "The rock around you becomes invisible.",
                       "uuid": str(uuid.uuid4()), "version": [1, 0, 0],
                       "min_engine_version": [1, 21, 0]},
            "modules": [{"type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 0],
                         "description": "See through terrain"}],
            "metadata": {"authors": ["Fliflightmc"], "license": "All Rights Reserved"},
        }, f, indent=2, ensure_ascii=False)

    blocks = {"format_version": "1.20.0"}
    for b in BEDROCK_BLOCS:
        blocks[b] = {"blockshape": "invisible"}
    with open(os.path.join(st, "blocks.json"), "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=2, ensure_ascii=False)

    os.makedirs(os.path.join(st, "ui"), exist_ok=True)
    with open(os.path.join(st, "ui", "hud_screen.json"), "w", encoding="utf-8") as f:
        json.dump({"namespace": "hud", "vignette_renderer": {"ignored": True}}, f, indent=2)
    print(f"    blocks.json : {len(BEDROCK_BLOCS)} blocs invisibles")

    icone(256).save(os.path.join(st, "pack_icon.png"))
    out = os.path.join(PACKS, BED_SLUG)
    os.makedirs(os.path.join(out, "files"), exist_ok=True)
    mc = f"{BED_SLUG}-1.0.0.mcpack"
    zp = os.path.join(out, "files", mc)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, names in os.walk(st):
            for n in names:
                full = os.path.join(root, n)
                z.write(full, os.path.relpath(full, st))
    shutil.copy(os.path.join(st, "pack_icon.png"), os.path.join(out, "pack_icon.png"))
    print(f"    + files/{mc}  ({os.path.getsize(zp)} octets)")
    return zp


def verifier(java, bed, ecrits):
    """Verification statique. Deux regles tirees d'un vrai echec : on ne compare pas une
    reference a la chaine qu'on a soi-meme ecrite (ca valide l'hypothese, pas le pack), et on
    exige que chaque texture citee existe reellement dans le jeu."""
    print("\n=== VERIFICATION ===")
    ok = True
    with zipfile.ZipFile(JAR) as jar:
        jar_noms = set(jar.namelist())
    tex_jeu = {n[len(TEX):-4] for n in jar_noms if n.startswith(TEX) and n.endswith(".png")}

    with zipfile.ZipFile(java) as z:
        noms = z.namelist()
        print(f"  JAVA : {len(noms)} entrees")
        for a, lib in [("pack.mcmeta", "pack.mcmeta"), ("pack.png", "icone")]:
            p = a in noms
            ok &= p
            print(f"     {'OK ' if p else 'NON'}  {lib}")

        shell = f"assets/minecraft/models/block/{ESPACE}/shell.json"
        j = json.loads(z.read(shell))

        def resoudre(ref):
            ns, sep, chemin = ref.partition(":")
            if not sep:
                ns, chemin = "minecraft", ref
            return f"assets/{ns}/models/{chemin}.json"

        ok &= j["parent"] == "minecraft:block/block" and len(j["elements"]) == 6
        culls = sum(1 for e in j["elements"] for f in e["faces"].values() if "cullface" in f)
        vars_faces = {f["texture"] for e in j["elements"] for f in e["faces"].values()}
        print(f"     coque : {len(j['elements'])} dalles, {culls} faces cullface, "
              f"variables distinctes {sorted(vars_faces)}")
        ok &= culls >= 20 and len(vars_faces) > 1

        mods = [n for n in noms if n.startswith("assets/minecraft/models/block/")
                and n.endswith(".json") and ESPACE not in n]
        pb = []
        for n in mods:
            m = json.loads(z.read(n))
            parent = m.get("parent")
            if not parent or resoudre(parent) not in noms:
                pb.append((n, f"parent irresolvable : {parent}"))
                continue
            t = m.get("textures") or {}
            if "particle" not in t:
                pb.append((n, "pas de texture 'particle' -> particules magenta"))
            for face in ("down", "up", "north", "south", "east", "west"):
                if face not in t:
                    pb.append((n, f"face {face} absente"))
                    break
            for k, v in t.items():
                if v.split(":", 1)[1] not in tex_jeu:
                    pb.append((n, f"texture inexistante : {v}"))
                    break
        print(f"     blocs couverts : {len(mods)} (attendu {len(ecrits)}) ; problemes : {len(pb)}")
        for n, r in pb[:8]:
            print(f"        {n} -> {r}")
        ok &= not pb and len(mods) == len(ecrits)

        # Garde-fou tire d'un vrai piege, pas d'une theorie : ecrire un gabarit (cube_all,
        # cube_column...) dans le pack ECRASE le modele vanilla dont heritent les minerais, et
        # les minerais deviennent transparents. On verifie donc les deux cotes : aucun gabarit,
        # aucun minerai dans le pack.
        def nom_court(chemin):
            return chemin[:-5].rsplit("/", 1)[-1]
        gabarits = [n for n in mods if GABARITS.match(nom_court(n))]
        minerais = [n for n in mods if MINERAIS.search(nom_court(n))]
        for ore in ("diamond_ore", "coal_ore", "deepslate_gold_ore", "nether_quartz_ore"):
            if f"assets/minecraft/models/block/{ore}.json" in noms:
                minerais.append(ore)
        print(f"     gabarits ecrits : {len(gabarits)} (doit etre 0) ; "
              f"minerais ecrits : {len(minerais)} (doit etre 0)")
        for n in (gabarits + minerais)[:6]:
            print(f"        A RETIRER : {n}")
        ok &= not gabarits and not minerais

        tex_bloc = [n for n in noms if n.startswith("assets/minecraft/textures/block/")]
        print(f"     textures de bloc modifiees : {len(tex_bloc)} (doit etre 0)")
        ok &= not tex_bloc

    with zipfile.ZipFile(bed) as z:
        noms = z.namelist()
        print(f"\n  BEDROCK : {len(noms)} entrees")
        for a in ["manifest.json", "blocks.json", "pack_icon.png", "ui/hud_screen.json"]:
            p = a in noms
            ok &= p
            print(f"     {'OK ' if p else 'NON'}  {a}")
        m = json.loads(z.read("manifest.json"))
        b = json.loads(z.read("blocks.json"))
        invis = [k for k, v in b.items() if isinstance(v, dict) and v.get("blockshape") == "invisible"]
        print(f"     blocs invisibles declares : {len(invis)}")
        print(f"     uuid unique : {'oui' if m['header']['uuid'] != m['modules'][0]['uuid'] else 'NON'}")
        ok &= m["header"]["uuid"] != m["modules"][0]["uuid"] and len(invis) > 40
        ic = Image.open(io.BytesIO(z.read("pack_icon.png")))
        print(f"     pack_icon : {ic.size[0]}x{ic.size[1]}")

    print(f"\n  RESULTAT : {'conforme' if ok else 'PROBLEME'}")
    return ok


if __name__ == "__main__":
    j = build_java()
    b = build_bedrock()
    verifier(j[0], b, j[1])
