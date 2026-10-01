"""Upload CurseForge gallery images for a project, in bulk.

CurseForge's image page (/project/<id>/images/upload) accepts ONE image at a time
and every field name is a hash regenerated on each page render, so the only way to
get the whole gallery in is to re-read the form before every upload:

    GET  -> parse name/id pairs -> POST multipart -> {"Status":"success"}

Usage:
    python scripts/cf_gallery_upload.py <project_id> <dossier_images> <captions.json>

`captions.json` maps a file name to the title shown under the image; files without
an entry are skipped, which keeps work-in-progress files out of the listing.

Cookie jar: this has to run as the logged-in user. Dump the legacy.curseforge.com
cookies from the browser into dist/cf_cookies.json first (CDP Network.getCookies).
"""
import glob
import json
import os
import re
import sys
import time

import requests

BASE = "https://legacy.curseforge.com"
TAG = re.compile(r"<(input|textarea|button)\b[^>]*>", re.I)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/141.0.0.0 Safari/537.36")


def champs(html):
    """Map field-<name> ids to (name, value) for every input/textarea/button."""
    out = {}
    for m in TAG.finditer(html):
        t = m.group(0)
        nm = re.search(r'\bname="([^"]+)"', t)
        idm = re.search(r'\bid="([^"]+)"', t)
        vm = re.search(r'\bvalue="([^"]*)"', t)
        if nm and idm:
            out[idm.group(1)] = (nm.group(1), vm.group(1) if vm else "")
    return out


def session(cookies_path):
    s = requests.Session()
    s.cookies.update(json.load(open(cookies_path, encoding="utf-8")))
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    return s


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    projet, dossier, captions_path = sys.argv[1], sys.argv[2], sys.argv[3]
    url = f"{BASE}/project/{projet}/images/upload"
    captions = json.load(open(captions_path, encoding="utf-8"))
    s = session(os.path.join(os.path.dirname(__file__), "..", "dist", "cf_cookies.json"))
    s.headers.update({"Referer": url, "Origin": BASE})

    images = [p for p in sorted(glob.glob(os.path.join(dossier, "*")))
              if os.path.basename(p) in captions]
    print(f"{len(images)} image(s) a envoyer vers le projet {projet}\n")

    for path in images:
        nom = os.path.basename(path)
        r = s.get(url, timeout=60)
        if r.status_code != 200:
            print(f"  {nom:26s} GET {r.status_code} - abandon")
            continue
        f = champs(r.text)
        data = {
            f["field-security-token"][0]: f["field-security-token"][1],
            f["field-authenticity-token"][0]: f["field-authenticity-token"][1],
            f["field-image-title"][0]: captions[nom],
            f["field-image-description"][0]: captions[nom].title(),
            f["field-upload"][0]: "y",
        }
        up = s.post(url, data=data,
                    files={f["field-attachment"][0]: (nom, open(path, "rb"), "image/png")},
                    timeout=180)
        try:
            rep = up.json()
            etat = rep.get("Status", up.status_code)
        except ValueError:
            etat = f"{up.status_code} (reponse non JSON)"
        print(f"  {nom:26s} {etat}")
        time.sleep(1.2)

    print("\nVerifier sur /minecraft/shaders/<slug>/screenshots (ou /texture-packs/...).")
    print("Attention : relancer le script duplique les images deja presentes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
