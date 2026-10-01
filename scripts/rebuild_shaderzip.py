import os, zipfile, shutil

SRC = r"C:\Users\user\fliflight-mods\shaderpacks\fliflight-vanilla-plus"
out = r"C:\Users\user\fliflight-mods\dist\shaderpacks\FliflightVanillaPlus-v0.3-Potato.zip"
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
shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.3-Potato.zip"))
for old in ["FliflightVanillaPlus-v0.2.zip"]:
    p = os.path.join(sp, old)
    if os.path.exists(p):
        os.remove(p)
        print("retire:", old)
# pour le test offline : OptiFine s'entete sur le nom deja selectionne
shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.2.zip"))
print(f"v0.3-Potato : {os.path.getsize(out)} B, {n} entrees")
