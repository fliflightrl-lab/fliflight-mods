#!/usr/bin/env bash
set -e
cd ~/fliflight-mods/work/shorts
mkdir -p music

# 1. phonk agressif (déjà généré)
curl -sL "https://d8j0ntlcm91z4.cloudfront.net/user_3Hpi2e0mw0tSXmncPEWhkWMjQ8j/hf_20260913_203450_22d2798c-c7cc-4aa0-9324-cfa132c3d4e4.m4a" -o music/phonk_agressif.m4a

# 2. phonk slowed/sombre
u2=$(higgsfield generate create sonilo_music --prompt "Dark slowed phonk, deep reverb 808 bass, pitched-down cowbell melody, atmospheric and menacing, heavy low end, eerie textures, 110 BPM, hypnotic, no vocals" --duration 30 --wait 2>&1 | tail -1)
curl -sL "$u2" -o music/phonk_slowed.m4a

# 3. R&B sombre
u3=$(higgsfield generate create sonilo_music --prompt "Dark moody R&B instrumental, lush synth pads, slow trap beat, melancholic atmosphere, cinematic, smooth deep bassline, 88 BPM, no vocals" --duration 30 --wait 2>&1 | tail -1)
curl -sL "$u3" -o music/rnb_sombre.m4a

# 4. rap FR trap
u4=$(higgsfield generate create sonilo_music --prompt "Dark trap beat for French rap, deep 808 bass, punchy drums, minor key piano riff, gritty urban atmosphere, 140 BPM, energetic, no vocals" --duration 30 --wait 2>&1 | tail -1)
curl -sL "$u4" -o music/rap_fr_trap.m4a

echo "=== RESULTATS ==="
for f in music/*.m4a; do
  d=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")
  sz=$(stat -c%s "$f")
  echo "$f: ${d}s ($((sz/1024)) KB)"
done
echo "DONE"
