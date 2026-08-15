#!/usr/bin/env python3
"""Check which fire textures exist in recent Minecraft versions (1.21.4 vs 1.21.8 vs latest)."""
import io, zipfile, json
import requests

# get version manifest, find relevant versions
m = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest_v2.json", timeout=60).json()
versions = {v["id"]: v["url"] for v in m["versions"]}
targets = ["1.21.4", "1.21.8"]
if "latest" in m:
    targets.append(m["latest"]["release"])

for ver in targets:
    if ver not in versions:
        print(f"{ver}: not in manifest"); continue
    vj = requests.get(versions[ver], timeout=60).json()
    jar_url = vj["downloads"]["client"]["url"]
    r = requests.get(jar_url, timeout=600, stream=True)
    buf = io.BytesIO()
    for chunk in r.iter_content(1024 * 256):
        buf.write(chunk)
    buf.seek(0)
    with zipfile.ZipFile(buf) as z:
        fires = sorted(n for n in z.namelist()
                       if n.startswith("assets/minecraft/textures/block/fire") and n.endswith(".png"))
        print(f"\n{ver} ({len(buf.getbuffer())/1e6:.0f}MB jar) fire textures:")
        for f in fires:
            print(f"  {f}")
