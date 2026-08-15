#!/usr/bin/env python3
"""Test the third CF key (Uvg9i4y...) on read + upload APIs."""
import requests

NEW = "$2a$10$Uvg9i4yTuWKGujo0hQbVaOvOb9i1b2QqikOmDB2pEk2hACZE5n08O"
PREV = "$2a$10$h0KqgEeSyhR/J.d2H02b/uaqQa/pdEGQf7OOsR2H9qSWxcSWg36ri"

print("different from previous key:", NEW != PREV)

# read API
r = requests.get("https://api.curseforge.com/v1/games", headers={"x-api-key": NEW}, timeout=30)
print(f"[read] /v1/games: HTTP {r.status_code}")

# upload API (probe)
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")
r = requests.post("https://minecraft.curseforge.com/api/projects/1334611/upload-file",
                  headers={"X-Api-Token": NEW},
                  files={"file": ("probe.png", png, "image/png"),
                         "metadata": (None, '{"changelog":"probe"}', "application/json")}, timeout=60)
print(f"[upload]: HTTP {r.status_code}")
print(f"  {r.text[:250]}")
