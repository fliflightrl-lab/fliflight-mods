#!/usr/bin/env python3
"""Detailed diagnosis of the new CF key (full response bodies)."""
import requests

NEW = "$2a$10$h0KqgEeSyhR/J.d2H02b/uaqQa/pdEGQf7OOsR2H9qSWxcSWg36ri"
OLD = "$2a$10$0cAQe9NETJqOcxHCXkqww.MFCOHSEoZxGYL1xtkUbStvCQLAgcXIm"

print(f"NEW length: {len(NEW)} chars")
print(f"OLD length: {len(OLD)} chars")
print()

for label, key in [("OLD", OLD), ("NEW", NEW)]:
    r = requests.get("https://api.curseforge.com/v1/games", headers={"x-api-key": key}, timeout=30)
    print(f"[read] {label}: HTTP {r.status_code}")
    print(f"  headers: {dict(r.headers).get('Content-Type')}")
    print(f"  body: {r.text[:300]}")
    print()

# also test a different endpoint with the new key
for ep in ["/v1/minecraft/version", "/v1/mods/1334611"]:
    r = requests.get(f"https://api.curseforge.com{ep}", headers={"x-api-key": NEW}, timeout=30)
    print(f"[read] NEW {ep}: HTTP {r.status_code}  body: {r.text[:200]}")
