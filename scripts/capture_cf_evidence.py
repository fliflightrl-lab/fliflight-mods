#!/usr/bin/env python3
"""Capture the RAW HTTP request + full response against the CurseForge upload
endpoint, with the API token REDACTED. Reproduces exactly what the pipeline
sends, so it can be forwarded to CF support as evidence."""
import json, os, io, zipfile, http.client

CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
TOKEN = CRED["curseforge"]["api_key"]
AUTHOR = CRED["curseforge"]["author_id"]
HOST = "minecraft.curseforge.com"
PATH = f"/api/projects/{AUTHOR}/upload-file"
RED = "REDACTED_$2a$10$..."

def redact(s: str) -> str:
    # hide every lookalike bcrypt token fragment too, just in case
    out = s.replace(TOKEN, RED)
    import re
    out = re.sub(r"\$2[aby]\$10\$[A-Za-z0-9./]{50,}", RED, out)
    return out

def dump(conn, req_line, headers, body=None):
    print("=" * 70)
    print("RAW REQUEST (token redacted)")
    print("-" * 70)
    print(req_line)
    for k, v in headers.items():
        print(f"{k}: {v if k.lower() != 'x-api-token' else RED}")
    if body is not None:
        print()
        print(redact(body[:400].decode("latin-1")))
        print("... [body truncated for display, sent in full]")
    print()
    print("FULL RESPONSE")
    print("-" * 70)
    conn.request(req_line.split()[0], PATH.split("?")[0], body=body, headers=headers)
    resp = conn.getresponse()
    print(f"HTTP {resp.status} {resp.reason}")
    for k, v in resp.getheaders():
        print(f"{k}: {v}")
    print()
    print(redact(resp.read().decode("utf-8", "replace")))
    print()

# ---- 1) POST multipart upload (exactly what the pipeline sends) ----
dummy = io.BytesIO()
with zipfile.ZipFile(dummy, "w") as z:
    z.writestr("pack.mcmeta", '{"pack":{"pack_format":46,"description":"test"}}')
dummy.seek(0)
boundary = "----fliflight-test-boundary"
parts = []
meta = json.dumps({
    "changelog": "test", "changelogType": "text",
    "displayName": "test", "gameVersions": [12656],
    "releaseType": "release",
})
parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="metadata"\r\n\r\n{meta}\r\n')
parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.zip"\r\nContent-Type: application/zip\r\n\r\n')
body = ("".join(parts)).encode() + dummy.getvalue() + f'\r\n--{boundary}--\r\n'.encode()

conn = http.client.HTTPSConnection(HOST, timeout=30)
dump(conn,
     f"POST {PATH} HTTP/1.1",
     {
         "Host": HOST,
         "X-Api-Token": TOKEN,
         "User-Agent": "fliflight-mods/1.0",
         "Accept": "*/*",
         "Content-Type": f"multipart/form-data; boundary={boundary}",
         "Content-Length": str(len(body)),
     },
     body)

# ---- 2) read-only GET on the SAME host (proves auth check, not the body) ----
conn = http.client.HTTPSConnection(HOST, timeout=30)
dump(conn,
     f"GET {PATH} HTTP/1.1",
     {
         "Host": HOST,
         "X-Api-Token": TOKEN,
         "User-Agent": "fliflight-mods/1.0",
         "Accept": "*/*",
     })
