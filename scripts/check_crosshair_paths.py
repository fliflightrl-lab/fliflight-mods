#!/usr/bin/env python3
"""Find the crosshair texture path in 1.21.4, 1.21.8, and 26.2."""
import io, zipfile
import requests

m = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json", timeout=60).json()
versions = {v["id"]: v["url"] for v in m["versions"]}

for ver in ["1.21.4", "1.21.8"]:
    vj = requests.get(versions[ver], timeout=60).json()
    r = requests.get(vj["downloads"]["client"]["url"], timeout=600, stream=True)
    buf = io.BytesIO()
    for chunk in r.iter_content(1024 * 256):
        buf.write(chunk)
    buf.seek(0)
    with zipfile.ZipFile(buf) as z:
        hits = sorted(n for n in z.namelist() if "crosshair" in n.lower())
        print(f"\n=== {ver} — crosshair files ===")
        for h in hits:
            print(f"  {h}")
