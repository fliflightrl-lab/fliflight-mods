#!/usr/bin/env python3
"""Re-test the upload API with the NEW key (now confirmed working on read)."""
import requests

NEW = "$2a$10$h0KqgEeSyhR/J.d2H02b/uaqQa/pdEGQf7OOsR2H9qSWxcSWg36ri"
PID = 1334611  # visible ores

png = bytes.fromhex("89504e470d0a1a0a0000000d494844520000000100000001080600000"
                     "01f15c4890000000d49444154789c626001000000ffff03000006000557bfabd40000000049454e44ae426082")

# probe upload: valid-ish metadata, tiny file. We only care whether AUTH passes.
metadata = '{"changelog":"probe","changelogType":"markdown","displayName":"probe","gameVersions":[10731],"releaseType":"alpha"}'
r = requests.post(f"https://minecraft.curseforge.com/api/projects/{PID}/upload-file",
                  headers={"X-Api-Token": NEW},
                  files={"file": ("probe.png", png, "image/png"),
                         "metadata": (None, metadata, "application/json")},
                  timeout=60)
print(f"upload API: HTTP {r.status_code}")
print(f"body: {r.text[:500]}")
print()
if "malformed" in r.text.lower():
    print(">> STILL 'malformed' — key rejected by upload endpoint")
else:
    print(">> NOT 'malformed' — key ACCEPTED by upload endpoint (auth passed)!")
