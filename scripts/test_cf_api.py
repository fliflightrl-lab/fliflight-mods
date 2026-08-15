#!/usr/bin/env python3
"""Test the CurseForge API key (read API) the user provided."""
import json, sys
import requests

KEY = "$2a$10$0cAQe9NETJqOcxHCXkqww.MFCOHSEoZxGYL1xtkUbStvCQLAgcXIm"

print("Testing key:", KEY[:12] + "...")
tests = [
    ("GET /v1/games",        "https://api.curseforge.com/v1/games"),
    ("GET /v1/minecraft/version", "https://api.curseforge.com/v1/minecraft/version"),
    ("GET /v1/mods/1334611", "https://api.curseforge.com/v1/mods/1334611"),
]

ok_all = True
for label, url in tests:
    try:
        r = requests.get(url, headers={"x-api-key": KEY}, timeout=30)
        body = r.text[:300]
        print(f"\n{label}\n  HTTP {r.status_code}")
        if r.status_code == 200:
            try:
                j = r.json()
                if "data" in j:
                    d = j["data"]
                    if isinstance(d, list):
                        print(f"  OK - data is list of {len(d)} items")
                    elif isinstance(d, dict):
                        print(f"  OK - data keys: {list(d.keys())[:8]}")
                else:
                    print(f"  OK - response keys: {list(j.keys())[:8]}")
            except Exception:
                print(f"  (non-JSON) {body[:200]}")
        else:
            print(f"  FAIL: {body[:200]}")
            ok_all = False
    except Exception as e:
        print(f"\n{label}\n  ERROR: {e}")
        ok_all = False

print("\n" + ("=" * 50))
print("RESULT:", "KEY WORKS (read API)" if ok_all else "KEY FAILED - TELL USER")
