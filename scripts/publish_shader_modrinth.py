"""Publie le shader pack sur Modrinth.

Etapes : creer le projet (brouillon) -> icone -> galerie (avec titres) -> version
-> soumettre a la moderation. Reprend exactement l'approche des autres scripts
de publication du depot (meme schema d'appel, meme licence).

Sources lues :
  dist/shader_meta.json        metadonnees (nom, slug, categories, chargeurs, versions)
  dist/shader_body.md          la fiche
  dist/shader_icon/*.png       l'icone (512)
  dist/shader_gallery/*.png    les captures legendees
  dist/shader_captions.json    titre de chaque capture
  dist/shaderpacks/*.zip       le fichier du pack

Usage:
  python scripts/publish_shader_modrinth.py --dry-run   # n'appelle rien, montre tout
  python scripts/publish_shader_modrinth.py             # publie
"""

import argparse
import glob
import json
import os
import sys

import requests

BASE = r"C:\Users\user\fliflight-mods"
DIST = os.path.join(BASE, "dist")
CRED = os.path.join(os.path.expanduser("~"), ".config", "fliflightmc", "credentials.json")
API = "https://api.modrinth.com/v2"
LICENSE = "LicenseRef-All-Rights-Reserved"   # meme licence que les autres projets


def load():
    meta = json.load(open(os.path.join(DIST, "shader_meta.json"), encoding="utf-8"))
    body = open(os.path.join(DIST, "shader_body.md"), encoding="utf-8").read()
    caps_path = os.path.join(DIST, "shader_captions.json")
    caps = json.load(open(caps_path, encoding="utf-8")) if os.path.isfile(caps_path) else {}

    zips = sorted(glob.glob(os.path.join(DIST, "shaderpacks", "*.zip")))
    icons = sorted(glob.glob(os.path.join(DIST, "shader_icon", "*-512.png")))
    gallery = sorted(glob.glob(os.path.join(DIST, "shader_gallery", "*.png")))
    return meta, body, caps, zips, icons, gallery


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta, body, caps, zips, icons, gallery = load()

    print("=" * 70)
    print("  PUBLICATION MODRINTH - shader pack")
    print("=" * 70)
    print(f"  nom          : {meta['title']}")
    print(f"  slug         : {meta['slug']}")
    print(f"  type         : {meta['project_type']}")
    print(f"  resume       : {meta['description']}")
    print(f"  categories   : {', '.join(meta['categories'])}")
    print(f"  chargeurs    : {', '.join(meta['loaders'])}")
    print(f"  versions     : {meta['game_versions'][0]} -> {meta['game_versions'][-1]}"
          f" ({len(meta['game_versions'])})")
    print(f"  licence      : {LICENSE}")
    print(f"  fiche        : {len(body)} caracteres")
    print(f"  icone        : {[os.path.basename(i) for i in icons] or 'MANQUANTE'}")
    print(f"  fichier      : {[os.path.basename(z) for z in zips] or 'MANQUANT'}")
    print(f"  galerie      : {len(gallery)} image(s)")
    for g in gallery:
        print(f"      {os.path.basename(g)}  「{caps.get(os.path.basename(g), '(sans titre)')}」")

    missing = []
    if not zips:
        missing.append("le zip du pack (dist/shaderpacks/*.zip)")
    if not icons:
        missing.append("l'icone (dist/shader_icon/*-512.png)")
    if missing:
        print("\n  MANQUE : " + " ; ".join(missing))
        return 1

    r = requests.get(f"{API}/project/{meta['slug']}", timeout=20)
    if r.status_code == 200:
        print(f"\n  /!\\ le slug '{meta['slug']}' existe deja sur Modrinth : {r.json()['id']}")
        print("      on mettra a jour ce projet au lieu d'en creer un.")
    elif r.status_code != 404:
        print(f"\n  verification du slug : {r.status_code} {r.text[:120]}")

    if args.dry_run:
        print("\n  --dry-run : aucun appel a l'API effectue.")
        return 0

    cred = json.load(open(CRED, encoding="utf-8"))
    hdr = {"Authorization": cred["modrinth"]["token"]}

    # 1. creer le projet (brouillon), comme les autres scripts du depot
    proj = {
        "slug": meta["slug"], "title": meta["title"], "description": meta["description"],
        "categories": meta["categories"], "game_versions": meta["game_versions"],
        "license_id": LICENSE, "license_url": None, "project_type": meta["project_type"],
        "client_side": meta["client_side"], "server_side": meta["server_side"],
        "body": body, "issues_url": None, "source_url": None, "wiki_url": None,
        "discord_url": None, "donation_urls": meta.get("donation_urls", []),
        "initial_versions": [], "is_draft": True,
    }
    r = requests.post(f"{API}/project", headers=hdr,
                      files={"data": (None, json.dumps(proj), "application/json")}, timeout=60)
    print(f"  creer le projet : {r.status_code} {r.text[:150]}")
    if r.status_code not in (200, 201):
        return 1
    pid = r.json()["id"]
    print(f"    id projet : {pid}")

    # 2. icone
    icon = icons[0]
    r = requests.patch(f"{API}/project/{pid}/icon?ext=png",
                       headers={**hdr, "Content-Type": "image/png"},
                       data=open(icon, "rb").read(), timeout=60)
    print(f"  icone : {r.status_code}")

    # 3. galerie, avec titre par image
    for i, g in enumerate(gallery):
        name = os.path.basename(g)
        r = requests.post(f"{API}/project/{pid}/gallery?ext=png&featured={str(i == 0).lower()}&ordering={i}",
                          headers={**hdr, "Content-Type": "image/png"},
                          data=open(g, "rb").read(), timeout=120)
        print(f"  galerie[{i}] {name} : {r.status_code}")
        if r.status_code == 200:
            url = r.json()[-1]["url"]
            title = caps.get(name, "")
            if title:
                r2 = requests.patch(f"{API}/project/{pid}/gallery?url={url}", headers=hdr,
                                    json={"title": title, "description": "", "featured": i == 0},
                                    timeout=30)
                print(f"      titre «{title}» : {r2.status_code}")

    # 4. version
    zip_path = zips[-1]
    fname = os.path.basename(zip_path)
    ver = {
        "project_id": pid, "name": f"v{meta['version_number']}",
        "version_number": meta["version_number"],
        "changelog": "First release.", "dependencies": [],
        "game_versions": meta["game_versions"], "version_type": meta["version_type"],
        "loaders": meta["loaders"], "featured": True,
        "file_parts": [fname], "primary_file": fname,
    }
    with open(zip_path, "rb") as f:
        r = requests.post(f"{API}/version", headers=hdr, timeout=300,
                          files={"data": (None, json.dumps(ver), "application/json"),
                                 fname: (fname, f, "application/zip")})
    print(f"  version {meta['version_number']} : {r.status_code} {r.text[:150]}")
    if r.status_code not in (200, 201):
        return 1

    # 5. soumettre a la moderation
    r = requests.patch(f"{API}/project/{pid}", headers=hdr, json={"status": "processing"}, timeout=30)
    print(f"  soumettre : {r.status_code}")

    meta["modrinth_id"] = pid
    json.dump(meta, open(os.path.join(DIST, "shader_meta.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"\n  URL : https://modrinth.com/shader/{meta['slug']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
