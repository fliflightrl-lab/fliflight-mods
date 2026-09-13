#!/usr/bin/env python3
"""Extract 12 victory clips (lead-in fight + victory) from the rush."""
import os, subprocess

RUSH = "C:/Users/user/Desktop/Youtube jingle montage miniature/Montage/Rush video/2026-09-13 19-08-00.mp4"
BASE = os.path.expanduser("~/fliflight-mods/work/rush")
OUT = f"{BASE}/wins"
os.makedirs(OUT, exist_ok=True)

# victory timestamps (mm:ss) from green scan
WINS = [
    "03:06", "07:32", "12:20", "14:54", "19:20", "24:12",
    "28:14", "34:16", "42:08", "51:50", "60:42", "64:34",
]

def tos(s):
    m, ss = s.split(":")
    return int(m) * 60 + int(ss)

LEAD = 16   # seconds of fight before victory
DUR = 24    # total clip length (lead + 8s after victory)

for i, w in enumerate(WINS, 1):
    v = tos(w)
    start = v - LEAD
    out = f"{OUT}/win_{i:02d}_{w.replace(':','')}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(DUR),
                    "-i", RUSH, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-c:a", "aac", out], check=True)
    print(out, f"({start//60:02d}:{start%60:02d} +{DUR}s)")
print("DONE")
