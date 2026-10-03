#!/usr/bin/env python3
"""Build the Fliflight Xray packs — one Java, one Bedrock.

Both were designed after READING two third-party packs the user supplied as references
(a Bedrock .mcpack and a Java .zip). No file is copied from either; only the techniques were
learned, then implemented from scratch, and the block lists are my own.

WHAT THE REFERENCES TAUGHT — and one expensive dead end:

  Java. My first attempt blanked the TEXTURES of the occluding blocks (alpha 0). That does not
  work: an opaque block is rendered with the "solid" material, which ignores alpha and paints
  the raw RGB — so transparent stone would have shown up as BLACK stone. The proof is in a
  working Xray pack already installed on this machine: it ships 484 blockstates and 823 models
  and exactly ZERO block textures. The trick is geometry, not colour:
    a thin 0.5-unit shell is placed on each of the six faces of the block, and every face
    carries "cullface" — so a face is only drawn when the neighbouring block is NOT opaque,
    and disappears against other terrain. Result: solid rock becomes a faint lattice of edges,
    while ores (which keep their normal models) show through it.
  We implement the same idea with one file per block instead of two, by overriding the block's
  MODEL directly (the vanilla blockstate already points at it), plus "light_emission": 15 so
  the terrain is lit and caves stay readable.

  Bedrock. A resource pack can declare a block's SHAPE as "invisible" in blocks.json — no
  textures, no models. The reference combines that with emissive ores via *_mer texture sets;
  we skip the emissive half (it would mean authoring matching metalness/emissive maps for every
  ore) because hiding the host rock already exposes the ores. The reference's own block list
  also omits dirt/sand/grass entirely; ours covers the full terrain set on purpose.

  Both packs additionally neutralise the overlays that block the view (pumpkin blur, underwater
  tint, vignette). In Java those ARE alpha-tested textures, so blanking them is correct there.

Run:  python scripts/build_xray.py
"""
import io
import json
import os
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

# Blocs de terrain a rendre transparents a la vue. (nom du modele -> texture a plaquer)
JAVA_BLOCS = {
    "stone": "block/stone", "granite": "block/granite", "diorite": "block/diorite",
    "andesite": "block/andesite", "cobblestone": "block/cobblestone",
    "mossy_cobblestone": "block/mossy_cobblestone", "stone_bricks": "block/stone_bricks",
    "deepslate": "block/deepslate", "tuff": "block/tuff", "calcite": "block/calcite",
    "dripstone_block": "block/dripstone_block", "netherrack": "block/netherrack",
    "basalt": "block/basalt_side", "blackstone": "block/blackstone",
    "end_stone": "block/end_stone", "obsidian": "block/obsidian",
    "dirt": "block/dirt", "coarse_dirt": "block/coarse_dirt", "rooted_dirt": "block/rooted_dirt",
    "grass_block": "block/grass_block_top", "podzol": "block/podzol_top",
    "mycelium": "block/mycelium_top", "gravel": "block/gravel", "clay": "block/clay",
    "sand": "block/sand", "red_sand": "block/red_sand", "sandstone": "block/sandstone",
    "red_sandstone": "block/red_sandstone", "mud": "block/mud", "packed_mud": "block/packed_mud",
    "soul_sand": "block/soul_sand", "soul_soil": "block/soul_soil",
    "moss_block": "block/moss_block", "snow_block": "block/snow", "powder_snow": "block/powder_snow",
    "oak_leaves": "block/oak_leaves", "spruce_leaves": "block/spruce_leaves",
    "birch_leaves": "block/birch_leaves", "jungle_leaves": "block/jungle_leaves",
    "acacia_leaves": "block/acacia_leaves", "dark_oak_leaves": "block/dark_oak_leaves",
    "mangrove_leaves": "block/mangrove_leaves", "cherry_leaves": "block/cherry_leaves",
    "azalea_leaves": "block/azalea_leaves",
    "flowering_azalea_leaves": "block/flowering_azalea_leaves",
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
    "mushroom_stem", "muddy_mangrove_roots", "reeds",
]

# Overlays qui masquent la vue. En Java ce sont de vraies textures a canal alpha : les vider
# fonctionne ici (contrairement aux textures de blocs, voir l'en-tete).
OVERLAYS = ["misc/pumpkinblur", "misc/underwater", "misc/vignette", "misc/powder_snow_outline"]


def vanilla(rel):
    with zipfile.ZipFile(JAR) as z:
        return z.read(TEX + rel + ".png")


def coque():
    """Les 6 dalles fines : 0,5 unite d'epaisseur, une par face, chacune avec 'cullface'.

    C'est le coeur du pack. Une face portant 'cullface' n'est dessinee que si le bloc voisin
    de ce cote n'est pas opaque — donc entre deux blocs de pierre rien n'est dessine du tout,
    et le terrain disparait au profit des minerais.
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
    elements = []
    for f, t, faces in plans:
        elements.append({
            "from": f, "to": t,
            "light_emission": 15,
            "faces": {c: {"uv": uv, "texture": "#all", "cullface": c}
                      for c, uv in faces.items()},
        })
    return {"parent": "minecraft:block/block", "ambientocclusion": False, "elements": elements}


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
    # size // 32 place exactement 16 texels dans la largeur affichee.
    ech = max(1, size // 32)
    iw = ih = art.size[0] * ech
    off = ((size - iw) // 2, (size - ih) // 2)

    glow = Image.new("L", (size, size), 0)
    pad = max(3, int(max(iw, ih) * 0.30))
    ImageDraw.Draw(glow).rounded_rectangle(
        [off[0]-pad, off[1]-pad, off[0]+iw+pad, off[1]+ih+pad],
        radius=int(max(iw, ih)*0.30), fill=125)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(3, max(iw, ih)//8)))
    cyan = Image.new("RGB", (size, size), (90, 220, 235))
    img = Image.blend(img, Image.composite(cyan, img, glow), 0.42)

    art = art.resize((iw, ih), Image.NEAREST)
    # Ombre portee et contour dessines a l'echelle d'UN pixel d'icone (u), pas a l'echelle du
    # fichier : tout trait plus fin disparait a l'affichage 32 px. L'ancien cadre etait trace en
    # size//160, soit un cinquieme de pixel d'icone — invisible en jeu, il ne servait a rien.
    u = max(1, size // 32)
    d = ImageDraw.Draw(img)
    d.rectangle([off[0] + u, off[1] + u, off[0] + iw - 1 + u, off[1] + ih - 1 + u], fill=(6, 7, 10))
    img.paste(art, off, art)
    ImageDraw.Draw(img).rectangle(
        [off[0] - u, off[1] - u, off[0] + iw - 1 + u, off[1] + ih - 1 + u],
        outline=(30, 34, 40), width=u)
    return img


def build_java():
    print("\n--- JAVA ---")
    st = os.path.join(BUILD, JAVA_SLUG)
    if os.path.isdir(st):
        shutil.rmtree(st)
    racine = os.path.join(st, "assets", "minecraft")
    os.makedirs(os.path.join(racine, "models", "block", ESPACE), exist_ok=True)

    with open(os.path.join(racine, "models", "block", ESPACE, "shell.json"), "w", encoding="utf-8") as f:
        json.dump(coque(), f, indent=1)
    print(f"    coque : models/block/{ESPACE}/shell.json (6 dalles, cullface)")

    faits, absents = [], []
    for nom, tex in sorted(JAVA_BLOCS.items()):
        try:
            vanilla(tex)
        except KeyError:
            absents.append(tex)
            continue
        with open(os.path.join(racine, "models", "block", nom + ".json"), "w", encoding="utf-8") as f:
            # Le parent est "minecraft:block/..." et non "<ESPACE>:block/..." : la coque est
            # rangee sous assets/minecraft/, donc elle appartient au namespace "minecraft".
            # Se tromper ici ne casse pas le chargement du pack, ca produit juste un avertissement
            # "Missing block model" et des blocs rendus en damier violet. Vu en jeu, pas en theorie.
            json.dump({"parent": f"minecraft:block/{ESPACE}/shell", "textures": {"all": tex}}, f, indent=1)
        faits.append(nom)
    print(f"    {len(faits)} modeles de bloc remplaces"
          + (f" | textures introuvables, ignores : {absents}" if absents else ""))

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
        # On annonce 46 (1.21.4) comme minimum et non 15 : les modeles utilisent
        # "light_emission", un champ de modele de bloc apparu en 1.21.2, et 1.21.4 est la seule
        # version sur laquelle ce pack a ete charge. Annoncer plus large serait une affirmation
        # que rien ne soutient.
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
    return zp, faits


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


def verifier(java, bed, blocs):
    """Verification statique : structure, JSON valides, references resolues, textures existantes."""
    print("\n=== VERIFICATION ===")
    ok = True
    with zipfile.ZipFile(JAR) as jar:
        jar_noms = set(jar.namelist())

    with zipfile.ZipFile(java) as z:
        noms = z.namelist()
        print(f"  JAVA : {len(noms)} entrees")
        for a, libelle in [("pack.mcmeta", "pack.mcmeta"), ("pack.png", "icone")]:
            p = a in noms
            ok &= p
            print(f"     {'OK ' if p else 'NON'}  {libelle}")

        shell = f"assets/minecraft/models/block/{ESPACE}/shell.json"
        j = json.loads(z.read(shell))
        ok &= j["parent"] == "minecraft:block/block" and len(j["elements"]) == 6
        culls = sum(1 for e in j["elements"] for f in e["faces"].values() if "cullface" in f)
        print(f"     coque : {len(j['elements'])} dalles, {culls} faces avec cullface")
        ok &= culls >= 20

        mods = [n for n in noms if n.startswith("assets/minecraft/models/block/")
                and n.endswith(".json") and ESPACE not in n]

        def resoudre(ref):
            """Traduit une reference de modele en chemin reel dans le pack.

            C'est le controle qui manquait : on ne compare plus le parent a la valeur qu'on a
            soi-meme ecrite (ce qui validait une hypothese fausse), on verifie qu'il pointe sur
            un fichier qui existe vraiment.
            """
            ns, sep, chemin = ref.partition(":")
            if not sep:
                ns, chemin = "minecraft", ref
            return f"assets/{ns}/models/{chemin}.json"

        manquants = []
        for n in mods:
            m = json.loads(z.read(n))
            parent = m.get("parent")
            if not parent:
                manquants.append((n, "aucun parent"))
            elif resoudre(parent) not in noms:
                manquants.append((n, f"parent irresolvable : {parent} -> {resoudre(parent)}"))
            tex = m["textures"]["all"]
            if f"assets/minecraft/textures/{tex}.png" not in jar_noms:
                manquants.append((n, f"texture absente du jeu : {tex}"))
        print(f"     modeles de bloc remplaces : {len(mods)} ; en erreur : {len(manquants)}")
        for n, r in manquants[:6]:
            print(f"        {n} -> {r}")
        ok &= not manquants
        ok &= len(mods) == len(blocs)

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
