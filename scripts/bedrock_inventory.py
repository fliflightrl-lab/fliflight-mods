#!/usr/bin/env python3
"""Inventory of all Bedrock-ready packs -> JSON + combined zip of the .mcpack files.

Usage: python3 scripts/bedrock_inventory.py
Outputs:
  dist/bedrock/bedrock-projects.json   (structured inventory)
  dist/bedrock/Bedrock-All-Packs.zip   (all .mcpack bundled)
"""
import datetime, json, os, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_mcpack import map_path, PREFIX

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = os.path.join(ROOT, "packs")
BEDROCK = os.path.join(ROOT, "dist", "bedrock")


def analyse(java_zip):
    """-> (ported[(java,bedrock)], dropped[], gui[])"""
    with zipfile.ZipFile(java_zip) as z:
        names = z.namelist()
    ported, dropped, gui = [], [], []
    for n in names:
        if n.endswith("/") or not n.startswith(PREFIX) or n.endswith(".mcmeta"):
            continue
        rel = n[len(PREFIX):]
        if "textures/gui/" in n:
            gui.append(rel)
            continue
        bp = map_path(rel)
        (ported.append((rel, bp)) if bp else dropped.append(rel))
    return ported, dropped, gui


def main():
    projects, skipped = [], []
    for slug in sorted(os.listdir(PACKS)):
        pdir = os.path.join(PACKS, slug)
        mp = os.path.join(pdir, "manifest.json")
        if not os.path.exists(mp):
            continue
        m = json.load(open(mp, encoding="utf-8"))
        files = os.listdir(os.path.join(pdir, "files"))
        if not files:
            continue
        ported, dropped, gui = analyse(os.path.join(pdir, "files", files[0]))
        mcpack = os.path.join(BEDROCK, f"{slug}.mcpack")
        if m.get("project_type") != "resourcepack":
            skipped.append({"slug": slug, "reason": "mod Java"})
            continue
        if gui:
            skipped.append({"slug": slug, "reason": "textures HUD/gui (crosshair/hotbar)"})
            continue
        if not ported:
            skipped.append({"slug": slug, "reason": "aucune texture remplaçable sur Bedrock"})
            continue
        projects.append({
            "slug": slug,
            "name": m["name"],
            "summary": m.get("summary", ""),
            "curseforge_id": m.get("curseforge_id"),
            "modrinth_id": m.get("modrinth_id"),
            "mcpack": f"dist/bedrock/{slug}.mcpack",
            "mcpack_bytes": os.path.getsize(mcpack) if os.path.exists(mcpack) else 0,
            "mcpack_built": os.path.exists(mcpack),
            "textures_ported": len(ported),
            "textures_skipped": len(dropped),
            "bedrock_textures": [bp for _, bp in ported],
        })

    inv = {
        "generated_at": datetime.datetime.now().isoformat(),
        "game": "Minecraft Bedrock",
        "count": len(projects),
        "total_bytes": sum(p["mcpack_bytes"] for p in projects),
        "projects": projects,
        "not_portable": skipped,
    }
    os.makedirs(BEDROCK, exist_ok=True)
    jpath = os.path.join(BEDROCK, "bedrock-projects.json")
    json.dump(inv, open(jpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    zpath = os.path.join(BEDROCK, "Bedrock-All-Packs.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in projects:
            fp = os.path.join(ROOT, p["mcpack"])
            if os.path.exists(fp):
                z.write(fp, os.path.basename(fp))
        z.write(jpath, "bedrock-projects.json")

    print(f"OK {len(projects)} projets Bedrock -> {jpath}")
    print(f"   archive -> {zpath} ({os.path.getsize(zpath)} octets)")
    for p in projects:
        print(f"   {p['name'][:40]:42} {p['textures_ported']:>3} textures  "
              f"{p['mcpack_bytes']:>7} B  {'OK' if p['mcpack_built'] else 'MANQUANT'}")
    print(f"\nNon portables: {len(skipped)}")
    for s in skipped:
        print(f"   {s['slug']:44} - {s['reason']}")


if __name__ == "__main__":
    main()
