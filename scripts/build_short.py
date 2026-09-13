#!/usr/bin/env python3
"""Build a vertical 9:16 gaming short from a 16:9 clip + TTS voiceover + ASS captions."""
import os, subprocess, sys

BASE = os.path.expanduser("~/fliflight-mods/work")
WD = f"{BASE}/shorts"          # working dir (ass + tts + output)
os.makedirs(WD, exist_ok=True)


def ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(path, lines):
    """lines: list of (start, end, style, text)"""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Impact,80,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,8,4,8,50,50,130,1
Style: Cap,Arial,58,&H00FFFFFF,&H000000FF,&H00101010,&H00000000,-1,0,0,0,100,100,0,0,1,6,3,8,50,50,140,1
Style: Win,Impact,88,&H0000FF00,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,8,4,8,50,50,140,1
Style: CTA,Impact,68,&H0000FFFF,&H000000FF,&H00202020,&H00000000,-1,0,0,0,100,100,1,0,1,7,4,2,40,40,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = ""
    for start, end, style, text in lines:
        body += f"Dialogue: 0,{ts(start)},{ts(end)},{style},,0,0,0,,{text}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + body)


def build_short(spec):
    src = spec["src"]                 # absolute path to 16:9 clip
    dur = spec["dur"]
    ass = spec["ass"]                 # filename in WD
    voices = spec["voices"]           # list of (filename, delay_s)
    out = spec["out"]
    build_ass(f"{WD}/{ass}", spec["captions"])

    inputs = ["-i", src]
    for vf, _ in voices:
        inputs += ["-i", f"{WD}/{vf}"]

    # video: blurred bg + centered 16:9 fg + subtitles
    fc = ("[0:v]split=2[bg][fg];"
          "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          "gblur=sigma=28,eq=brightness=-0.16:saturation=0.85[bb];"
          "[fg]scale=1080:-2[ff];"
          "[bb][ff]overlay=0:656[b];"
          f"[b]subtitles={ass}[v]")
    # audio: game audio ducked + voices
    amix_parts = ["[0:a]volume=0.30[g]"]
    labels = "[g]"
    for i, (vf, delay) in enumerate(voices, start=1):
        ms = int(delay * 1000)
        amix_parts.append(f"[{i}:a]adelay={ms}|{ms},volume=1.9[a{i}]")
        labels += f"[a{i}]"
    fc += ";" + ";".join(amix_parts) + f";{labels}amix=inputs={len(voices)+1}:normalize=0:dropout_transition=0,alimiter=limit=0.95[a]"

    cmd = (["ffmpeg", "-y", "-loglevel", "error"] + inputs +
           ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-t", str(dur), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out])
    print("running ffmpeg...")
    subprocess.run(cmd, check=True, cwd=WD)
    print("OUT:", out)


SHORT1 = {
    "src": os.path.expanduser("~/fliflight-mods/work/rush/clips/clipB_victoire1855.mp4"),
    "dur": 29,
    "ass": "short1.ass",
    "out": "short1_crosshair.mp4",
    "voices": [("s1_v1.mp3", 0.4), ("s1_v2.mp3", 4.3), ("s1_v3.mp3", 18.3), ("s1_v4.mp3", 21.2)],
    "captions": [
        (0.4, 4.2, "Hook", r"TON CROSSHAIR EST\NLA RAISON DE TES MISSES"),
        (4.3, 11.0, "Cap", r"UN POINT. PROPRE.\NTU VOIS TA CIBLE, TU LA TOUCHES."),
        (18.0, 21.0, "Win", r"ET LÀ...\NTU GAGNES."),
        (21.3, 28.0, "CTA", r"GRATUIT SUR CURSEFORGE\NLIEN EN BIO"),
    ],
}

SHORT2 = {
    "src": os.path.expanduser("~/fliflight-mods/work/rush/clips/clipE2_fail7120.mp4"),
    "dur": 33,
    "ass": "short2.ass",
    "out": "short2_meme.mp4",
    "voices": [("s2_v1.mp3", 0.4), ("s2_v2.mp3", 3.9), ("s2_v3.mp3", 19.0), ("s2_v4.mp3", 24.3)],
    "captions": [
        (0.4, 3.7, "Hook", r"POV : TU JOUES\NTON 1V1 LE PLUS IMPORTANT"),
        (3.9, 12.5, "Cap", r"TU TOUCHES. TU ES CHAUD."),
        (12.5, 19.0, "Cap", r"PLUS QU'UN COUP\nÀ PORTER..."),
        (19.0, 24.2, "Win", r"ET LÀ...\NTU PERDS."),
        (24.3, 32.5, "CTA", r"MAIS TON CROSSHAIR EST CLEAN\NGRATUIT — LIEN EN BIO"),
    ],
}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    if which == "1":
        build_short(SHORT1)
    elif which == "2":
        build_short(SHORT2)
