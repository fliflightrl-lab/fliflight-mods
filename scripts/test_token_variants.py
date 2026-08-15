#!/usr/bin/env python3
"""Test upload API with token format variations."""
import requests

KEY = "$2a$10$h0KqgEeSyhR/J.d2H02b/uaqQa/pdEGQf7OOsR2H9qSWxcSWg36ri"
PID = 1334611
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")

metadata = '{"changelog":"probe","changelogType":"markdown","displayName":"probe","gameVersions":[10731],"releaseType":"alpha"}'

variants = [
    ("full key X-Api-Token", {"X-Api-Token": KEY}),
    ("no prefix X-Api-Token", {"X-Api-Token": KEY.replace("$2a$10$", "")}),
    ("x-api-key header", {"x-api-key": KEY}),
]
for label, headers in variants:
    try:
        r = requests.post(f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
                          headers=headers,
                          files={"file": ("probe.png", png, "image/png"),
                                 "metadata": (None, metadata, "application/json")}, timeout=60)
        body = r.text[:200].replace("\n", " ")
        print(f"{label}: HTTP {r.status_code}  {body}")
    except Exception as e:
        print(f"{label}: ERROR {e}")

# also try the game version endpoint with the upload API base + X-Api-Token (to isolate auth)
r = requests.get("https://minecraft.curseforge.com/api/game/versions?cache=true",
                 headers={"X-Api-Token": KEY}, timeout=60)
print(f"\n[isolate auth] GET /game/versions (upload API): HTTP {r.status_code}  {r.text[:200]}")
