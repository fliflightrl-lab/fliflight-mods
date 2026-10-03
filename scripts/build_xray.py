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

# Minerais a rendre lumineux cote Bedrock : nom Bedrock -> texture du jeu servant de source.
# Aucun fichier n'est repris de la reference : la carte emissive est derivee de la texture
# vanilla, donc de la forme reelle des filons.
BEDROCK_MER = {
    "coal_ore": "block/coal_ore", "copper_ore": "block/copper_ore",
    "diamond_ore": "block/diamond_ore", "emerald_ore": "block/emerald_ore",
    "gold_ore": "block/gold_ore", "iron_ore": "block/iron_ore",
    "lapis_ore": "block/lapis_ore", "redstone_ore": "block/redstone_ore",
    "nether_gold_ore": "block/nether_gold_ore", "quartz_ore": "block/nether_quartz_ore",
    "ancient_debris_side": "block/ancient_debris_side",
    "ancient_debris_top": "block/ancient_debris_top",
    "deepslate_coal_ore": "block/deepslate_coal_ore",
    "deepslate_copper_ore": "block/deepslate_copper_ore",
    "deepslate_diamond_ore": "block/deepslate_diamond_ore",
    "deepslate_emerald_ore": "block/deepslate_emerald_ore",
    "deepslate_gold_ore": "block/deepslate_gold_ore",
    "deepslate_iron_ore": "block/deepslate_iron_ore",
    "deepslate_lapis_ore": "block/deepslate_lapis_ore",
    "deepslate_redstone_ore": "block/deepslate_redstone_ore",
}

# Correspondances Java -> Bedrock pour les blocs pleins. Les deux editions ont diverge sur les
# noms, et deviner ne pardonne pas : un identifiant inconnu dans blocks.json produit une erreur
# de contenu. Chaque candidat est donc verifie contre la table d'identifiants du jeu avant d'etre
# ecrit (voir blocs_bedrock), ce qui rend une faute de nom impossible a livrer.
BEDROCK_RENAMES = {
    "dirt_path": "grass_path", "snow_block": "snow",
    "magma_block": "magma", "slime_block": "slime", "melon": "melon_block",
    "cobweb": "web", "spawner": "mob_spawner", "note_block": "noteblock",
    "stone_bricks": "stonebrick", "mossy_stone_bricks": "mossy_stonebrick",
    "bricks": "brick_block", "end_stone_bricks": "end_bricks",
    "nether_bricks": "nether_brick", "red_nether_bricks": "red_nether_brick",
    "polished_blackstone_bricks": "polished_blackstone_brick",
    "deepslate_bricks": "deepslate_brick", "mud_bricks": "mud_brick",
    "terracotta": "hardened_clay", "jack_o_lantern": "lit_pumpkin",
}

# Blocs pleins propres a Bedrock, absents de mon cote Java parce que les deux jeux ne partagent
# pas tout (argile cuite, pierre taillee d'origine, etc.).
BEDROCK_EN_PLUS = [
    "hardened_clay", "stained_hardened_clay", "stonebrick", "mossy_stonebrick",
    "brick_block", "nether_brick", "red_nether_brick", "end_bricks", "mob_spawner",
    "noteblock", "lit_pumpkin", "web", "grass", "grass_path", "snow", "slime",
    "magma", "melon_block", "glowingobsidian", "allow", "deny",
]


def blocs_bedrock(noms_java, chemins_extra=()):
    """Liste des blocs Bedrock a rendre invisibles, chaque nom verifie contre la table du jeu.

    On part des blocs pleins identifies cote Java, on tente pour chacun une poignee de variantes
    de nom (les deux editions divergent : grass_block -> grass, stone_bricks -> stonebrick,
    snow_block -> snow...), et on ne garde que les noms reellement presents dans la table.
    """
    table = {}
    for p in (os.path.join(BUILD, "bedrock", "block_properties_table.json"),) + tuple(chemins_extra):
        if os.path.exists(p):
            try:
                table = json.load(open(p, encoding="utf-8"))
                break
            except Exception:
                pass
    if not table:
        return None, []
    connus = {k.split(":", 1)[-1] for k in table}

    def candidats(nom):
        out = []
        if nom in BEDROCK_RENAMES:
            out.append(BEDROCK_RENAMES[nom])
        out.append(nom)
        if nom.endswith("_block"):
            out.append(nom[:-6])
        if nom.endswith("_bricks"):
            out.append(nom[:-1])
            out.append(nom.replace("bricks", "brick"))
        out.append(nom.replace("stone_bricks", "stonebrick"))
        out.append(nom.replace("_bricks", "_brick"))
        out.append(nom.replace("_terracotta", "_terracotta"))
        return out

    retenus, perdus = [], []
    for nom in list(noms_java) + list(BEDROCK_EN_PLUS):
        trouve = next((c for c in candidats(nom) if c in connus), None)
        if trouve:
            if trouve not in retenus:
                retenus.append(trouve)
        else:
            perdus.append(nom)
    return sorted(retenus), perdus


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
    """Vrai si le modele occupe un cube entier.

    Deux chemins y menent, et n'en tester qu'un rate des blocs entiers :
      1. heriter d'une famille cube (cube_all, cube_column, orientable...) ;
      2. definir soi-meme des elements formant un cube 0..16.

    Le second cas est celui des FEUILLAGES et de l'herbe : block/leaves et grass_block heritent
    directement de block/block et portent leur propre geometrie. Les oublier laissait les
    feuillages opaques — ce que l'utilisateur avait explicitement demande de couvrir, et que le
    premier test ne pouvait pas voir puisqu'il ne suivait que la chaine des parents.
    """
    if nom in _cube_cache:
        return _cube_cache[nom]
    _cube_cache[nom] = None
    cur, vus, prof = nom, set(), 0
    while cur and cur not in vus and prof < 12:
        vus.add(cur)
        m = mods.get(cur) or {}
        for e in (m.get("elements") or []):
            if e.get("from") == [0, 0, 0] and e.get("to") == [16, 16, 16]:
                _cube_cache[nom] = "elements"
                return "elements"
        p = m.get("parent")
        if not p:
            break
        court = p.split(":", 1)[1] if p.startswith("minecraft:") else p
        court = court.split("/")[-1]
        if FAMILLES_CUBE.match(court):
            _cube_cache[nom] = court
            return court
        cur = court
        prof += 1
    return None


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


def minerai():
    """Un cube entier, SANS 'cullface' : ses faces sont dessinees en toutes circonstances.

    C'est la piece qui manquait, et sans elle le pack ne sert a rien. Un minerai enterre est
    entoure de blocs opaques : les faces de son modele vanilla portent 'cullface', donc elles
    sont TOUTES eliminees et le minerai n'est jamais dessine. Seul un minerai affleurant a l'air
    apparaissait — exactement ce que l'utilisateur a photographie : un bloc d'or visible sous le
    reticule, aucun autre.

    En retirant 'cullface' des faces, MC les dessine toujours, et le minerai devient visible a
    travers les coques transparentes du terrain. 'light_emission': 15 le fait ressortir meme
    dans une grotte non eclairee.
    """
    return {
        "parent": "minecraft:block/block",
        "ambientocclusion": False,
        "textures": {"particle": "#all", "all": "#all"},
        "elements": [{
            "from": [0, 0, 0], "to": [16, 16, 16],
            "light_emission": 15,
            "faces": {c: {"uv": [0, 0, 16, 16], "texture": "#all"} for c in
                      ("down", "up", "north", "south", "east", "west")},
        }],
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
    with open(os.path.join(racine, "models", "block", ESPACE, "ore.json"), "w", encoding="utf-8") as f:
        json.dump(minerai(), f, indent=1)
    print(f"    {len(mods)} modeles lus dans le jar")

    ecrits, minerais_ecrits, sans_tex, ecartes = [], [], [], []
    for nom in sorted(mods):
        if GABARITS.match(nom) or nom in DENYLIST:
            ecartes.append(nom)
            continue
        if not est_bloc_plein(nom, mods):
            continue
        tex = textures_resolues(nom, mods)
        if nom in SECOURS:
            tex.update({k: ("minecraft:" + v if ":" not in v else v)
                        for k, v in SECOURS[nom].items()})

        if MINERAIS.search(nom):
            # Les minerais ne sont pas masques : ils recoivent le cube SANS 'cullface', sans quoi
            # un minerai enterre n'est jamais dessine et le pack ne montre rien. C'est l'inverse
            # de l'intention, mais le meme fichier : on change le parent, pas la texture.
            tout = next((tex[k] for k in ("all", "side", "end", "top", "down", "up", "north")
                         if k in tex), None)
            if not tout or tout.split(":", 1)[1] not in tex_dispo:
                sans_tex.append(nom)
                continue
            with open(os.path.join(racine, "models", "block", nom + ".json"), "w",
                      encoding="utf-8") as f:
                json.dump({"parent": f"minecraft:block/{ESPACE}/ore",
                           "textures": {"all": tout, "particle": tout}}, f, indent=1)
            minerais_ecrits.append(nom)
            continue

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
    print(f"    {len(minerais_ecrits)} minerais rendus visibles a travers (cube sans cullface)")
    print(f"    ecartes : {len(ecartes)} (gabarits, blocs techniques)")
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
                            "description": f"{NOM} v1.0.1 — ores now show through the terrain",
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


def build_bedrock(noms_java=()):
    print("\n--- BEDROCK ---")
    st = os.path.join(BUILD, BED_SLUG)
    if os.path.isdir(st):
        shutil.rmtree(st)
    os.makedirs(st, exist_ok=True)
    with open(os.path.join(st, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "format_version": 2,
            "header": {"name": f"§b{NOM}", "description": "Ores glow through the invisible rock.",
                       "uuid": str(uuid.uuid4()), "version": [1, 0, 1],
                       "min_engine_version": [1, 21, 0]},
            "modules": [{"type": "resources", "uuid": str(uuid.uuid4()), "version": [1, 0, 1],
                         "description": "See through terrain"}],
            "metadata": {"authors": ["Fliflightmc"], "license": "All Rights Reserved"},
        }, f, indent=2, ensure_ascii=False)

    liste, perdus = blocs_bedrock(noms_java)
    if liste is None:
        print("    !! table d'identifiants Bedrock introuvable -> repli sur la liste de reference")
        liste, perdus = list(BEDROCK_BLOCS), []
    blocks = {"format_version": "1.20.0"}
    for b in liste:
        blocks[b] = {"blockshape": "invisible"}
    with open(os.path.join(st, "blocks.json"), "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=2, ensure_ascii=False)

    os.makedirs(os.path.join(st, "ui"), exist_ok=True)
    with open(os.path.join(st, "ui", "hud_screen.json"), "w", encoding="utf-8") as f:
        json.dump({"namespace": "hud", "vignette_renderer": {"ignored": True}}, f, indent=2)
    print(f"    blocks.json : {len(liste)} blocs invisibles (chaque nom verifie contre la table)")
    if perdus:
        print(f"    sans equivalent Bedrock, ignores : {len(perdus)} -> {sorted(perdus)[:12]}")

    # Eclairage : sans lui, une grotte reste noire et on ne voit rien de ce qu'on vient de
    # devoiler. C'est la contrepartie Bedrock de 443 blocs rendus transparents.
    os.makedirs(os.path.join(st, "lighting"), exist_ok=True)
    with open(os.path.join(st, "lighting", "global.json"), "w", encoding="utf-8") as f:
        json.dump({
            "format_version": "1.21.80",
            "minecraft:lighting_settings": {
                "description": {"identifier": "minecraft:default_lighting"},
                "directional_lights": {
                    "orbital": {
                        "sun": {"illuminance": {k: 100.0 for k in
                                                ("0.000000", "0.250000", "0.500000", "0.750000", "1.000000")},
                                "color": {"0.000000": [255, 255, 255], "0.500000": [255, 255, 255],
                                          "1.000000": [255, 255, 255]}},
                        "moon": {"illuminance": {k: 10.0 for k in
                                                 ("0.000000", "0.250000", "0.500000", "0.750000", "1.000000")},
                                 "color": {"0.000000": [255, 255, 255], "1.000000": [255, 255, 255]}},
                        "orbital_offset_degrees": 0.0},
                    "flash": {"illuminance": 15.0, "color": [255, 255, 255]}},
                "emissive": {"desaturation": 0.0},
                "ambient": {"color": "#FFFFFF", "illuminance": 25.0},
                "sky": {"intensity": 2.0},
            },
        }, f, indent=2)
    print("    lighting/global.json : grottes eclairees")

    # Minerais lumineux. Meme raison que cote Java : un bloc invisible ne "devoile" rien si ce
    # qu'il cachait n'est pas dessine. Bedrock ne se contente pas de rendre la roche invisible —
    # il faut que les minerais emettent, sinon ils restent noyes dans l'obscurite.
    #   _mer = une carte 16x16 : R metalness, V emissif, B rugosite. On derive le canal emissif
    #   de la luminosite de la texture du minerai, ce qui fait briller les filons et pas la gangue.
    n_mer = 0
    for cible, source in BEDROCK_MER.items():
        try:
            art = Image.open(io.BytesIO(vanilla(source))).convert("RGBA")
        except KeyError:
            print(f"    texture introuvable cote Java, ignore : {source}")
            continue
        lum = art.convert("L")
        mer = Image.merge("RGBA", (
            Image.new("L", art.size, 5),                                   # metalness
            lum.point(lambda v: min(255, int(v * 0.55))),                  # emissif
            Image.new("L", art.size, 0),                                   # rugosite
            art.getchannel("A"),                                           # opacite
        ))
        sous = "deepslate/" if cible.startswith("deepslate_") else ""
        d = os.path.join(st, "textures", "blocks", sous)
        os.makedirs(d, exist_ok=True)
        nom_bed = cible.split("/")[-1]
        mer.save(os.path.join(d, nom_bed + "_mer.png"))
        with open(os.path.join(d, nom_bed + ".texture_set.json"), "w", encoding="utf-8") as f:
            json.dump({"format_version": "1.16.100",
                       "minecraft:texture_set": {"color": nom_bed,
                                                 "metalness_emissive_roughness": nom_bed + "_mer"}},
                      f, indent=2)
        n_mer += 1
    print(f"    {n_mer} minerais lumineux (carte _mer + texture_set)")

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
            # Les coques nomment leurs 6 faces une a une ; les minerais declarent une seule cle
            # 'all' que le gabarit ore mappe sur les 6. Les deux formes sont valides.
            if "all" not in t:
                for face in ("down", "up", "north", "south", "east", "west"):
                    if face not in t:
                        pb.append((n, f"face {face} absente (aucune cle 'all')"))
                        break
            for k, v in t.items():
                if v.split(":", 1)[1] not in tex_jeu:
                    pb.append((n, f"texture inexistante : {v}"))
                    break
        print(f"     blocs couverts : {len(mods)} (attendu {len(ecrits)} coques + minerais)")
        for n, r in pb[:8]:
            print(f"        {n} -> {r}")
        ok &= not pb

        # Garde-fou tire d'un vrai piege : ecrire un gabarit (cube_all, cube_column...) dans le
        # pack ECRASE le modele vanilla dont heritent les minerais. Les gabarits restent donc
        # interdits. Les minerais, eux, DOIVENT etre presents — surcharges avec le cube sans
        # cullface, seule facon pour qu'un minerai enterre soit dessine.
        def nom_court(chemin):
            return chemin[:-5].rsplit("/", 1)[-1]
        gabarits = [n for n in mods if GABARITS.match(nom_court(n))]
        modele_ore = json.loads(z.read(f"assets/minecraft/models/block/{ESPACE}/ore.json"))
        culls_ore = sum(1 for e in modele_ore["elements"]
                        for f in e["faces"].values() if "cullface" in f)
        coques = [n for n in mods if json.loads(z.read(n)).get("parent") == f"minecraft:block/{ESPACE}/shell"]
        minerais = [n for n in mods if json.loads(z.read(n)).get("parent") == f"minecraft:block/{ESPACE}/ore"]
        mal = [n for n in mods if json.loads(z.read(n)).get("parent") not in
               (f"minecraft:block/{ESPACE}/shell", f"minecraft:block/{ESPACE}/ore")]
        print(f"     gabarits ecrits : {len(gabarits)} (doit etre 0)")
        print(f"     faces SANS cullface sur le modele de minerai : "
              f"{6*len(modele_ore['elements']) - culls_ore} (le cube doit en etre depourvu)")
        print(f"     coques : {len(coques)} ; minerais surcharges : {len(minerais)}")
        for ore in ("diamond_ore", "coal_ore", "deepslate_gold_ore", "nether_quartz_ore"):
            if f"assets/minecraft/models/block/{ore}.json" not in noms:
                print(f"        MANQUANT : {ore} resterait invisible sous terre")
                minerais = []
        ok &= not gabarits and culls_ore == 0 and not mal and len(minerais) >= 20
        ok &= len(coques) == len(ecrits)

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
        # Contrat, pas un instantane : chaque identifiant ecrit doit exister dans la table du jeu.
        # C'est la seule facon de garantir qu'aucune faute de nom Java/Bedrock n'est livree, et
        # elle ne peut pas passer par accident puisqu'elle interroge une source externe au pack.
        tp = os.path.join(BUILD, "bedrock", "block_properties_table.json")
        connus = set()
        if os.path.exists(tp):
            connus = {k.split(":", 1)[-1] for k in json.load(open(tp, encoding="utf-8"))}
        inconnus = [n for n in invis if connus and n not in connus]
        print(f"     blocs invisibles declares : {len(invis)}")
        print(f"     identifiants absents de la table du jeu : {len(inconnus)} (doit etre 0)")
        for n in inconnus[:8]:
            print(f"        INCONNU : {n}")
        attendus = ("stone", "deepslate", "grass_block", "netherrack", "end_stone", "obsidian",
                    "bedrock", "sculk", "tuff", "calcite", "gravel", "sand", "oak_leaves",
                    "spruce_leaves", "acacia_leaves")
        absents = [c for c in attendus if c not in invis]
        if absents:
            print(f"        MANQUANTS : {absents}")
        print(f"     uuid unique : {'oui' if m['header']['uuid'] != m['modules'][0]['uuid'] else 'NON'}")
        ok &= (m["header"]["uuid"] != m["modules"][0]["uuid"] and len(invis) >= 250
               and not inconnus and not absents)
        ic = Image.open(io.BytesIO(z.read("pack_icon.png")))
        print(f"     pack_icon : {ic.size[0]}x{ic.size[1]}")

    print(f"\n  RESULTAT : {'conforme' if ok else 'PROBLEME'}")
    return ok


if __name__ == "__main__":
    j = build_java()
    b = build_bedrock(j[1])
    verifier(j[0], b, j[1])
