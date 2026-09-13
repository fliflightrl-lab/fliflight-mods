#!/usr/bin/env python3
"""Build N vertical 9:16 shorts from victory clips: music bed + game SFX + text overlays, no VO."""
import os, subprocess, glob

BASE = os.path.expanduser("~/fliflight-mods/work")
WINS = f"{BASE}/rush/wins"
MUSIC = f"{BASE}/shorts/music_phonk.wav"
OUT = f"{BASE}/shorts"
os.makedirs(OUT, exist_ok=True)

# 12 punchy French hooks (écritures)
HOOKS = [
    "CE COMBAT ÉTAIT CHAUD",
    "IL PENSAIT GAGNER",
    "TROP RAPIDE POUR LUI",
    "LE DERNIER COUP",
    "POV : TU CLUTCH",
    "IL A RIEN PU FAIRE",
    "LE KILL PARFAIT",
    "INARRÊTABLE",
    "LA PRESSION MONTE",
    "ELLE EST POUR TOI",
    "UN SHOT, UN KILL",
    "ET BOOM.",
]

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
Style: CTA,Impact,66,&H0000FFFF,&H000000FF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,7,4,2,40,40,150,1

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
        (20.0, 24.0, "CTA", r"GRATUIT SUR CURSEFORGE\NLIEN EN BIO"),
    ]
    body = "".join(f"Dialogue: 0,{ts(a)},{ts(b)},{st},,0,0,0,,{tx}\n" for a, b, st, tx in lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(STYLES + body)

def build(clip, ass_name, out_name, idx):
    ass_path = f"{OUT}/{ass_name}"
    write_ass(ass_path, HOOKS[idx - 1])
    fc = (
        "[0:v]split=2[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "gblur=sigma=28,eq=brightness=-0.16:saturation=0.85[bb];"
        "[fg]scale=1080:-2[ff];"
        "[bb][ff]overlay=0:656[b];"
        f"[b]subtitles={ass_name}[v];"
        "[0:a]volume=0.50,apad[g];"
        "[1:a]volume=0.82,apad[m];"
        "[g][m]amix=inputs=2:normalize=0:dropout_transition=0,alimiter=limit=0.95[a]"
    )
    cmd = (["ffmpeg", "-y", "-loglevel", "error", "-i", clip, "-i", MUSIC,
            "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", "24", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", f"{OUT}/{out_name}"])
    subprocess.run(cmd, check=True, cwd=OUT)

clips = sorted(glob.glob(f"{WINS}/win_*.mp4"))
for i, clip in enumerate(clips, 1):
    out_name = f"short_w{i:02d}.mp4"
    build(clip, f"w{i:02d}.ass", out_name, i)
    print("built", out_name)
print("ALL DONE:", len(clips), "shorts")
