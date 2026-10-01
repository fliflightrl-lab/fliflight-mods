import os, zipfile, shutil

SRC = r"C:\Users\user\fliflight-mods\shaderpacks\fliflight-vanilla-plus"
out = r"C:\Users\user\fliflight-mods\dist\shaderpacks\FliflightVanillaPlus-v0.2.zip"
sp = r"C:\Users\user\AppData\Roaming\.minecraft\shaderpacks"

if os.path.exists(out):
    os.remove(out)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, fs in os.walk(SRC):
        for f in fs:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, SRC).replace(os.sep, "/")
            if rel.startswith("shaders/"):
                z.write(full, rel)

n = len(zipfile.ZipFile(out).namelist())
shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.2.zip"))
shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.1.zip"))
print(f"zip reconstruit: {os.path.getsize(out)} B, {n} entrees")
print("installe sous les 2 noms (v0.1 pour qu'OptiFine le charge)")
