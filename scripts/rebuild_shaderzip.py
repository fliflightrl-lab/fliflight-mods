import os, sys, zipfile, shutil

SRC = r"C:\Users\user\fliflight-mods\shaderpacks\fliflight-vanilla-plus"
CONFIG = os.path.join(SRC, "shaders", "lib", "config.glsl")
sp = r"C:\Users\user\AppData\Roaming\.minecraft\shaderpacks"

flags = {
    "HORIZON_HAZE": "--haze" in sys.argv,
    "SHARPEN": "--sharpen" in sys.argv,
}
test_build = "--test" in sys.argv

name = "ZZ-TEST.zip" if test_build else "FliflightVanillaPlus-v0.4-Potato.zip"
out = os.path.join(r"C:\Users\user\fliflight-mods\dist\shaderpacks", name)

txt = open(CONFIG, encoding="utf-8").read()
for flag, on in flags.items():
    off_line = f"\n//#define {flag}"
    on_line = f"\n#define {flag}"
    if on:
        txt = txt.replace(off_line, on_line)
    else:
        txt = txt.replace(on_line, off_line)
open(CONFIG, "w", encoding="utf-8", newline="\n").write(txt)

state = {f: ("ON " if f"\n#define {f}" in txt else "off") for f in flags}

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
if not test_build:
    # OptiFine s'entete sur le nom deja selectionne : on ecrase aussi l'ancien
    shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.3.1-Potato.zip"))
    shutil.copy2(out, os.path.join(sp, "FliflightVanillaPlus-v0.3-Potato.zip"))
print(f"{name} : {os.path.getsize(out)} B, {n} entrees | " + " ".join(f"{k}={v}" for k, v in state.items()))
