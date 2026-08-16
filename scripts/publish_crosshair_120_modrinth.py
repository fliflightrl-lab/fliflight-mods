import json, os, urllib.request

MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
BASE = "https://api.modrinth.com/v2"
REPO = os.path.expanduser("~/fliflight-mods")

FABRIC_API_ID = "P7dR8mSH"

# Project ids (from prior session)
PROJECT_ID = "o01bugzT"  # fliflight-custom-crosshair
FILE = os.path.join(REPO, "mods/custom-crosshair/build/libs/custom-crosshair-1.2.0.jar")

def multipart_post(url, data_json, file_field=None, file_path=None):
    boundary = "----fliflightv120"
    parts = []
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(b'Content-Disposition: form-data; name="data"\r\n')
    parts.append(b"Content-Type: application/json\r\n\r\n")
    parts.append(json.dumps(data_json).encode())
    parts.append(b"\r\n")
    if file_field and file_path:
        fname = os.path.basename(file_path)
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"\r\n'.encode())
        parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
        parts.append(open(file_path, "rb").read())
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", MR_TOKEN)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()

ver = {
    "project_id": PROJECT_ID,
    "name": "Custom Crosshair 1.2.0",
    "version_number": "1.2.0",
    "changelog": "Scrollable GUI, side preview, T crosshair, center dot, thickness-1 fix, Valorant preset fix.",
    "dependencies": [
        {"version_id": None, "project_id": FABRIC_API_ID, "dependency_type": "required"}
    ],
    "game_versions": ["1.21.4"],
    "version_type": "release",
    "loaders": ["fabric"],
    "featured": False,
    "file_parts": [os.path.basename(FILE)],
    "primary_file": os.path.basename(FILE),
}

status, body = multipart_post(f"{BASE}/version", ver, file_field=os.path.basename(FILE), file_path=FILE)
print("POST /version ->", status)
print("body:", body[:400])
