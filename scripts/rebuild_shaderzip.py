import os, sys, glob, zipfile, shutil

SRC = r"C:\Users\user\fliflight-mods\shaderpacks\fliflight-vanilla-plus"
CONFIG = os.path.join(SRC, "shaders", "lib", "config.glsl")
DIST = r"C:\Users\user\fliflight-mods\dist\shaderpacks"
SP = r"C:\Users\user\AppData\Roaming\.minecraft\shaderpacks"

flags = {
    "HORIZON_HAZE": "--haze" in sys.argv,
    "SHARPEN": "--sharpen" in sys.argv,
    "SHADOWS": "--shadows" in sys.argv,
}
test_build = "--test" in sys.argv

txt = open(CONFIG, encoding="utf-8").read()
for flag, on in flags.items():
    off_markers = [f"\n//#define {flag}", f"\n//#define {flag}   // DESACTIVE : artefact non resolu, a reactiver pour tester"]
    on_line = f"\n#define {flag}"
    if on:
        for off in off_markers:
            txt = txt.replace(off, on_line)
    else:
        # remet la forme commentee en gardant le commentaire explicatif s'il existe
        if f"\n//#define {flag}   // DESACTIVE" in txt:
            pass
        else:
            txt = txt.replace(on_line, f"\n//#define {flag}")
open(CONFIG, "w", encoding="utf-8", newline="\n").write(txt)

shadows_on = "\n#define SHADOWS" in txt
state = {f: ("ON " if f"\n#define {f}" in txt else "off") for f in flags}

name = "ZZ-TEST.zip" if test_build else "FliflightVanillaPlus-v0.5-Potato.zip"
out = os.path.join(DIST, name)
if os.path.exists(out):
    os.remove(out)

skipped = []
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for root, _, fs in os.walk(SRC):
        for f in fs:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, SRC).replace(os.sep, "/")
            if not rel.startswith("shaders/"):
                continue
            # sans SHADOWS, on n'embarque pas le programme d'ombre : OptiFine ne
            # fait alors AUCUNE passe d'ombre, ce qui est le seul vrai gain de perf.
            if not shadows_on and rel in ("shaders/shadow.vsh", "shaders/shadow.fsh"):
                skipped.append(rel)
                continue
            z.write(full, rel)

n = len(zipfile.ZipFile(out).namelist())

# INSTALLATION. OptiFine s'entete sur le nom deja selectionne : en mode test on ecrase
# TOUS les noms de pack fliflight presents, sinon le test valide l'ancien code.
loaded = [name] if test_build else [name]
if test_build:
    for p in glob.glob(os.path.join(SP, "FliflightVanillaPlus-*.zip")):
        loaded.append(os.path.basename(p))
else:
    for old in glob.glob(os.path.join(SP, "FliflightVanillaPlus-*.zip")):
        os.remove(old)
for t in set(loaded):
    shutil.copy2(out, os.path.join(SP, t))

print(f"{name} : {os.path.getsize(out)} B, {n} entrees | " + " ".join(f"{k}={v}" for k, v in state.items()))
print(f"  programme d'ombre embarque : {'oui' if shadows_on else 'NON (aucune passe d ombre)'}")
print(f"  ecrit sous : {sorted(set(loaded))}")
