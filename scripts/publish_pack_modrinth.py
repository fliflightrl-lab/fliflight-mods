#!/usr/bin/env python3
"""Publish a resource pack project to Modrinth from its manifest, end to end.

    python scripts/publish_pack_modrinth.py <slug>

Creates the project if it does not exist yet, then sets icon, gallery, version and the Ko-fi
donation link, and finally submits it for review. Re-running it on an existing project updates
it instead of failing.

API quirks baked in here, all found the hard way on earlier projects:
  - POST /project must be MULTIPART: files={"data": (None, json.dumps(payload), ...)}.
    A plain JSON body is rejected.
  - `categories` is REQUIRED at creation and capped at THREE. Four gives
    "Field categories failed validation with error: length" - the word "length" misleads, the
    cause is the count. Same cap on PATCH.
  - nested objects (donation_urls) do not survive the multipart create; they are applied by a
    JSON PATCH afterwards.
  - the donation platform id comes from a hyphenated enum: "ko-fi" works, "kofi" is refused
    with the misleading "each donation link must specify a donation platform".
  - the icon is set with PATCH (+?ext=png); PUT returns 404.
  - a gallery item is POSTed as raw bytes, then PATCHed by ?url=<.webp> to attach its title.
  - submission is PATCH {"status": "processing"} and can 400 with a `nags` array naming the
    exact blocking field; the nag is printed verbatim so it can be acted on.
  - the project title for Modrinth stays SHORT: a feature listed in the name is a 5.2
    rejection. The descriptive CurseForge name lives in the manifest; the part after the
    first " - " is dropped here.
"""
import json
import os
import sys

import requests

BASE = r"C:\Users\user\fliflight-mods"
API = "https://api.modrinth.com/v2"
CRED = os.path.join(os.path.expanduser("~"), ".config", "fliflightmc", "credentials.json")
TOKEN = json.load(open(CRED, encoding="utf-8"))["modrinth"]["token"]
HDR = {"Authorization": TOKEN}
LICENSE = "LicenseRef-All-Rights-Reserved"   # 'arr' is rejected: "Invalid SPDX license identifier"
DONATION = [{"id": "ko-fi", "platform": "Ko-fi", "url": "https://ko-fi.com/fliflight"}]

# gallery file name -> (title shown under the image, featured)
TITRES = {
    "01-cave-before-after.png": ("A cave, before and after", True),
    "02-night-before-after.png": ("The same spot at night, before and after", False),
    "03-nether.png": ("The Nether", False),
    "04-the-end.png": ("The End", False),
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    slug = sys.argv[1]
    d = os.path.join(BASE, "packs", slug)
    man = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))

    # the SHORT name goes to Modrinth; the descriptive CF name keeps its subtitle
    titre = man["name"].split(" - ")[0].strip()
    # Slug: prefix with the author to avoid the "Slug is already taken!" collision (the bare
    # product name is usually held by someone else), and stay consistent with the other packs.
    mslug = man.get("modrinth_slug") or slug
    print(f"projet : {titre!r}  slug Modrinth : {mslug}")
    print(f"  resume : {man['summary'][:90]}...")

    pid = man.get("modrinth_id")
    if not pid:
        payload = {
            "slug": mslug, "title": titre, "description": man["summary"],
            "categories": man["categories"][:3],          # REQUIRE et PLAFONNE a 3
            "license_id": LICENSE, "license_url": None,
            "project_type": "resourcepack",
            "client_side": "required", "server_side": "unsupported",
            "body": man["body"], "initial_versions": [], "is_draft": True,
        }
        r = requests.post(f"{API}/project", headers=HDR,
                          files={"data": (None, json.dumps(payload), "application/json")}, timeout=90)
        print(f"  creation : {r.status_code} {r.text[:160]}")
        if r.status_code not in (200, 201):
            return 1
        pid = r.json()["id"]
        print(f"    id : {pid}")
        man["modrinth_id"] = pid
        json.dump(man, open(os.path.join(d, "manifest.json"), "w", encoding="utf-8"),
                  indent=2, ensure_ascii=False)
    else:
        print(f"  projet existant : {pid}")

    # champs complexes : PATCH en JSON (le multipart les aplatit)
    patch = {"game_versions": man["version"]["game_versions"], "donation_urls": DONATION}
    r = requests.patch(f"{API}/project/{pid}", headers=HDR, json=patch, timeout=60)
    print(f"  versions + don : {r.status_code}")

    # icone
    icon = os.path.join(d, man["icon"])
    with open(icon, "rb") as f:
        r = requests.patch(f"{API}/project/{pid}/icon?ext=png", headers=HDR, data=f.read(), timeout=90)
    print(f"  icone : {r.status_code}")

    # galerie — IDEMPOTENT : on reutilise les entrees deja presentes au lieu d'en ajouter,
    # et on rattrape une entree sans titre laissee par une execution interrompue.
    gal = os.path.join(d, "gallery")
    vœux = man.get("gallery", [])
    existantes = requests.get(f"{API}/project/{pid}", headers=HDR, timeout=60).json().get("gallery", [])
    for i, nom in enumerate(vœux):
        p = os.path.join(gal, nom)
        if not os.path.exists(p):
            print(f"    {nom} : ABSENT"); continue
        titre_img, featured = TITRES.get(nom, (nom.rsplit('.', 1)[0], False))
        if i < len(existantes):
            url = existantes[i]["url"]           # deja en ligne : on repose juste le titre
            etat = "titre repose"
        else:
            with open(p, "rb") as f:
                r = requests.post(
                    f"{API}/project/{pid}/gallery?ext=png&featured={'true' if featured else 'false'}",
                    headers=HDR, data=f.read(), timeout=120)
            # le POST repond 204 SANS corps : l'URL se relit dans la galerie du projet
            url = None
            try:
                url = r.json().get("url")
            except ValueError:
                pass
            if url is None:
                g = requests.get(f"{API}/project/{pid}", headers=HDR, timeout=60).json().get("gallery", [])
                url = g[-1]["url"] if g else None
            etat = f"envoyee ({r.status_code})"
        if url:
            r2 = requests.patch(f"{API}/project/{pid}/gallery?url={url}", headers=HDR,
                                json={"title": titre_img, "description": "", "featured": featured},
                                timeout=60)
            print(f"    {nom} : {etat} puis titre {r2.status_code} — {titre_img!r}")

    # version + fichier — on ne renvoie pas une version deja presente
    zpath = os.path.join(d, "files", man["file"])
    deja = [v["version_number"] for v in
            requests.get(f"{API}/project/{pid}/version", headers=HDR, timeout=60).json()]
    if man["version"]["number"] in deja:
        print(f"  version {man['version']['number']} : deja en ligne, on ne renvoie pas")
    else:
        vdata = {"project_id": pid, "name": f"{man['name']} {man['version']['number']}",
                 "version_number": man["version"]["number"], "changelog": man["version"]["changelog"],
                 "dependencies": [], "game_versions": man["version"]["game_versions"],
                 "version_type": man["version"]["type"], "loaders": man["version"]["loaders"],
                 # REQUIS : sans cette liste, /version refuse avec "missing field file_parts"
                 "file_parts": ["file"],
                 "featured": True, "status": "listed"}
        with open(zpath, "rb") as f:
            r = requests.post(f"{API}/version", headers=HDR,
                              data={"data": json.dumps(vdata)},
                              files={"file": (man["file"], f, "application/zip")}, timeout=180)
        print(f"  version : {r.status_code} {r.text[:140]}")

    # soumission
    r = requests.patch(f"{API}/project/{pid}", headers=HDR, json={"status": "processing"}, timeout=60)
    print(f"  soumission : {r.status_code}")
    if r.status_code not in (200, 204):
        nags = r.json().get("details", {}).get("nags", [])
        for n in nags:
            print(f"    BLOCAGE {n.get('kind')} [{n.get('severity')}] {n.get('details')}")

    print(f"\n  https://modrinth.com/resourcepack/{mslug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
