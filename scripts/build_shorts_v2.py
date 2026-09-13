#!/usr/bin/env python3
"""Rebuild shorts v2: music-only audio, persistent CTA, end woosh+blur+zoom, no #7."""
import os, subprocess, glob

BASE = os.path.expanduser("~/fliflight-mods/work")
WINS = f"{BASE}/rush/wins"
MUSIC_DIR = f"{BASE}/shorts/music"
WHOOSH = f"{BASE}/shorts/whoosh.wav"
OUT = f"{BASE}/shorts"
os.makedirs(OUT, exist_ok=True)

AG = f"{MUSIC_DIR}/phonk_agressif.m4a"
SL = f"{MUSIC_DIR}/phonk_slowed.m4a"
TR = f"{MUSIC_DIR}/rap_fr_trap.m4a"
RB = f"{MUSIC_DIR}/rnb_sombre.m4a"

HOOKS = {1:"CE COMBAT ÉTAIT CHAUD", 2:"IL PENSAIT GAGNER", 3:"TROP RAPIDE POUR LUI",
         4:"LE DERNIER COUP", 5:"POV : TU CLUTCH", 6:"IL A RIEN PU FAIRE",
         8:"INARRÊTABLE", 9:"LA PRESSION MONTE", 10:"ELLE EST POUR TOI",
         11:"UN SHOT, UN KILL", 12:"ET BOOM."}

# music: R&B on win_01 only; rotate the 3 phonk/trap on the rest
NON_RB = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]
ROT = [AG, SL, TR]
MUSIC_FOR = {n: ROT[NON_RB.index(n) % 3] for n in NON_RB}
MUSIC_FOR[1] = RB

STYLES = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Impact,78,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,8,4,8,50,50,130,1
Style: Win,Impact,92,&H0000FF00,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,8,4,8,50,50,140,1
Style: CTA,Impact,44,&H0000FFFF,&H000000FF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,7,4,2,30,30,50,1
Style: EndZoom,Impact,116,&H0000FFFF,&H000000FF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,7,5,5,30,30,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def write_ass(path, hook):
    lines = [
        (0.3, 8.0, "Hook", hook),
        (15.0, 20.0, "Win", "GG WP"),
        (0.3, 20.8, "CTA", r"GRATUIT SUR CURSEFORGE · LIEN EN BIO"),
        (20.8, 24.0, "EndZoom",
         r"{\fad(120,0)\fscx40\fscy40\t(0,350,\fscx100,\fscy100)}GRATUIT SUR CURSEFORGE\NLIEN EN BIO"),
    ]
    body = "".join(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{tx}\n" for a, b, st, tx in lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(STYLES + body)

def build(clip, win_no, out_name, ass_name):
    write_ass(f"{OUT}/{ass_name}", HOOKS[win_no])
    music = MUSIC_FOR[win_no]
    fc = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "gblur=sigma=28,eq=brightness=-0.16:saturation=0.85[bb];"
        "[fg]scale=1080:-2[ff];"
        "[bb][ff]overlay=0:656[base];"
        "[base]split[bs][blsrc];"
        "[blsrc]gblur=sigma=22,format=rgba,fade=t=in:st=20.6:d=0.8:alpha=1[blf];"
        "[bs]format=rgba[bsr];"
        "[bsr][blf]overlay=0:0[base2];"
        f"[base2]subtitles={ass_name}[v];"
        "[1:a]volume=1.0,apad[m];"
        f"[2:a]adelay=20800|20800[a_w];"
        "[m][a_w]amix=inputs=2:normalize=0:dropout_transition=0,alimiter=limit=0.95[a]"
    )
    cmd = (["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", music, "-i", WHOOSH,
            "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", "24", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", f"{OUT}/{out_name}"])
    subprocess.run(cmd, check=True, cwd=OUT)

clips = sorted(glob.glob(f"{WINS}/win_*.mp4"))
built = 0
for clip in clips:
    win_no = int(clip.split("win_")[1][:2])
    if win_no == 7:
        continue
    out_name = f"short_w{win_no:02d}.mp4"
    build(clip, win_no, out_name, f"v2_{win_no:02d}.ass")
    print("built", out_name, "->", os.path.basename(MUSIC_FOR[win_no]))
    built += 1
print("TOTAL:", built, "shorts")
