import os, sys, zipfile, shutil

SRC = r"C:\Users\user\fliflight-mods\shaderpacks\fliflight-vanilla-plus"
CONFIG = os.path.join(SRC, "shaders", "lib", "config.glsl")
sp = r"C:\Users\user\AppData\Roaming\.minecraft\shaderpacks"

haze_on = "--haze" in sys.argv
name = "FliflightVanillaPlus-v0.3.1-Potato.zip" if not haze_on else "ZZ-TEST-haze-on.zip"
out = os.path.join(r"C:\Users\user\fliflight-mods\dist\shaderpacks", name)

# bascule le #define de la brume selon l'argument
txt = open(CONFIG, encoding="utf-8").read()
if haze_on:
    txt = txt.replace("\n//#define HORIZON_HAZE", "\n#define HORIZON_HAZE")
else:
    txt = txt.replace("\n#define HORIZON_HAZE", "\n//#define HORIZON_HAZE")
open(CONFIG, "w", encoding="utf-8", newline="\n").write(txt)
active = "\n#define HORIZON_HAZE" in txt

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
shutil.copy2(out, os.path.join(sp, name))
# OptiFine s'entete sur le nom deja selectionne : on ecrase aussi l'ancien
shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.3-Potato.zip"))
print(f"{name} : {os.path.getsize(out)} B, {n} entrees | HORIZON_HAZE {'ACTIF' if active else 'desactive'}")
