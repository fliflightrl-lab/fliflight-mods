#!/usr/bin/env python3
"""Compare the 'new' key to the stored one, and test it on the CF upload API."""
import json, requests

NEW = "$2a$10$0cAQe9NETJqOcxHCXkqww.MFCOHSEoZxGYL1xtkUbStvCQLAgcXIm"
STORED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))["curseforge"]["api_key"]

print("NEW    :", NEW)
print("STORED :", STORED)
print("\nIDENTICAL" if NEW == STORED else "\nDIFFERENT")

# test on upload API
png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")
PID = 1334611
r = requests.post(f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
                  headers={"X-Api-Token": NEW},
                  files={"file": ("probe.png", png, "image/png"),
                         "metadata": (None, '{"changelog":"test"}', "application/json")},
                  timeout=30)
print(f"\nupload API result: HTTP {r.status_code}")
print(r.text[:300])

# also confirm read API still accepts it
r2 = requests.get("https://api.curseforge.com/v1/games", headers={"x-api-key": NEW}, timeout=30)
print(f"\nread API result: HTTP {r2.status_code}")
