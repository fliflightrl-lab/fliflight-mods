#!/usr/bin/env python3
"""Generate a Bedrock .mcpack for every PORTABLE pack (texture-based).

Java-only packs (item models, HUD sprites) are skipped — Bedrock has no
equivalent. Output: dist/bedrock/<slug>.mcpack
"""
import json, os, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mcpack import build, map_path, PREFIX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
OUT = os.path.join(ROOT, "dist", "bedrock")


def classify(pdir, m):
    """-> (portable: bool, reason: str)"""
    if m.get("project_type") != "resourcepack":
        return False, "mod (Java only)"
    files = os.listdir(os.path.join(pdir, "files"))
    if not files:
        return False, "no file"
    with zipfile.ZipFile(os.path.join(pdir, "files", files[0])) as z:
        names = z.namelist()
    if any("textures/gui/" in n for n in names):
        return False, "HUD/crosshair sprites (no Bedrock equivalent)"
    mapped = [n for n in names if n.startswith(PREFIX)
              and n.endswith((".png", ".jpg")) and map_path(n[len(PREFIX):])]
    if not mapped:
        return False, "textures non remplaçables sur Bedrock (gérées par le moteur)"
    return True, f"{len(mapped)} textures"


def main():
    os.makedirs(OUT, exist_ok=True)
    generated, skipped = [], []
    for slug in sorted(os.listdir(PACKS)):
        pdir = os.path.join(PACKS, slug)
        mp = os.path.join(pdir, "manifest.json")
        if not os.path.exists(mp):
            continue
        m = json.load(open(mp, encoding="utf-8"))
        portable, reason = classify(pdir, m)
        if not portable:
            skipped.append((slug, reason))
            continue
        src = os.path.join(pdir, "files", os.listdir(os.path.join(pdir, "files"))[0])
        icon = None
        for ext in ("png", "jpg", "jpeg"):
            c = os.path.join(pdir, f"icon.{ext}")
            if os.path.exists(c):
                icon = c
                break
        build(src, os.path.join(OUT, f"{slug}.mcpack"), m["name"], m.get("summary", ""), icon)
        generated.append(slug)

    print(f"\nOK {len(generated)} .mcpack générés :")
    for s in generated:
        print("   ", s)
    print(f"\nSKIP {len(skipped)} non portables (exclus) :")
    for s, r in skipped:
        print(f"    {s:44} - {r}")


if __name__ == "__main__":
    main()
