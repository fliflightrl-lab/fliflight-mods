#!/usr/bin/env bash
# Teste la compilation GLSL du pack dans OptiFine, sans passer par le menu du jeu.
# Usage: bash scripts/of_compile_test.sh <etiquette>
# Lit logs/latest.log : "Program loaded: X" par programme, et les erreurs de compilation.
set -u

LABEL="${1:-test}"
MC="C:/Users/user/AppData/Roaming/.minecraft"
OF="$MC/libraries/optifine/OptiFine/1.21.4_HD_U_J4_pre2/OptiFine-1.21.4_HD_U_J4_pre2.jar"
LW="$MC/libraries/optifine/launchwrapper-of/2.3/launchwrapper-of-2.3.jar"
CPV=$(cat "C:/Users/user/AppData/Local/hermes/cache/scratch/mc_cp.txt")
LOG="C:/Users/user/AppData/Local/hermes/cache/scratch/of_${LABEL}.log"

taskkill /IM javaw.exe /F >/dev/null 2>&1
rm -f "$LOG"

( cd "$MC" && "C:/Program Files/Java/jdk-22/bin/javaw.exe" -Xmx2G \
  -Djava.library.path="$MC/versions/1.21.4/natives" \
  -cp "$OF;$LW;$CPV" \
  net.minecraft.launchwrapper.Launch --tweakClass optifine.OptiFineTweaker \
  --username Fliflight --version "1.21.4-OptiFine_HD_U_J4_pre2" \
  --gameDir "$MC" --assetsDir "$MC/assets" --assetIndex 19 \
  --uuid 58ecc73a68573344827127c8e75d94ce --accessToken 0 --userType legacy \
  --width 1280 --height 800 --quickPlaySingleplayer "test shader" > "$LOG" 2>&1 ) &

sleep 50

PROG=$(grep -ac "Program loaded" "$LOG")
ERR=$(grep -acE "Error compiling|Error linking|error C[0-9]" "$LOG")
echo "  [$LABEL] programmes: $PROG | erreurs: $ERR"
if [ "$ERR" -gt 0 ]; then
  grep -aE "Error compiling|error C[0-9]" "$LOG" | head -6 | cat -v
fi
grep -aiE "GL error|Exception in thread" "$LOG" | grep -aviE "Reflector|SharedSecrets|InaccessibleObject" | head -4 | cat -v

taskkill /IM javaw.exe /F >/dev/null 2>&1
# 0 probleme ET au moins 20 programmes charges = succes
if [ "$ERR" -eq 0 ] && [ "$PROG" -ge 20 ]; then echo "  [$LABEL] OK"; else echo "  [$LABEL] ECHEC"; exit 1; fi
