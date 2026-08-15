#!/usr/bin/env python3
"""Re-probe the CurseForge UPLOAD API with the current key (definitive answer for the user)."""
import requests

KEY = "$2a$10$0cAQe9NETJqOcxHCXkqww.MFCOHSEoZxGYL1xtkUbStvCQLAgcXIm"
# a real CF project id we own (visible ores)
PID = 1334611

# small probe file (1x1 png)
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")

probes = [
    ("upload API X-Api-Token", "POST",
     f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
     {"X-Api-Token": KEY}),
    ("upload API x-api-key", "POST",
     f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
     {"x-api-key": KEY}),
    ("upload API ?token=", "POST",
     f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file?token={KEY}",
     {}),
    ("modern api /upload (probe)", "POST",
     "https://api.curseforge.com/v1/mods/upload",
     {"x-api-key": KEY}),
]

for label, method, url, headers in probes:
    try:
        if method == "POST":
            r = requests.post(url, headers=headers,
                              files={"file": ("probe.png", png, "image/png"),
                                     "metadata": (None, '{"changelog":"test"}', "application/json")},
                              timeout=30)
        print(f"\n{label}\n  HTTP {r.status_code}\n  {r.text[:300]}")
    except Exception as e:
        print(f"\n{label}\n  ERROR: {e}")
