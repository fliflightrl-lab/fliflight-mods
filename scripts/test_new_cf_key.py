#!/usr/bin/env python3
"""Test the NEW CF key on both read and upload APIs."""
import json, requests

NEW = "$2a$10$h0KqgEeSyhR/J.d2H02b/uaqQa/pdEGQf7OOsR2H9qSWxcSWg36ri"
OLD = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))["curseforge"]["api_key"]

print("NEW    :", NEW)
print("OLD    :", OLD)
print("\nDIFFERENT" if NEW != OLD else "\nIDENTICAL (still the same key!)")

# 1. read API
r = requests.get("https://api.curseforge.com/v1/games", headers={"x-api-key": NEW}, timeout=30)
print(f"\n[1] read API /v1/games: HTTP {r.status_code}")

# 2. upload API (probe with minimal file + metadata)
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")
PID = 1334611  # visible ores (real project)
r = requests.post(f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
                  headers={"X-Api-Token": NEW},
                  files={"file": ("probe.png", png, "image/png"),
                         "metadata": (None, '{"changelog":"test","changelogType":"markdown","displayName":"test","gameVersions":[1],"releaseType":"alpha"}', "application/json")},
                  timeout=60)
print(f"\n[2] upload API: HTTP {r.status_code}")
print(f"    {r.text[:400]}")
