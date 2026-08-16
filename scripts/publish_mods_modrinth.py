import json, os, urllib.request

MR_TOKEN = "mrp_BuW9lcEew20QyOIPdCxYhx6APN5bCh0usOZbSycTsNHlmm2jhiFOrR3GOeLI"
BASE = "https://api.modrinth.com/v2"
REPO = os.path.expanduser("~/fliflight-mods")

FABRIC_API_ID = "P7dR8mSH"

MODS = [
    {
        "slug": "fliflight-pvphud",
        "title": "PvP HUD",
        "description": "Client-side PvP HUD for Minecraft: FPS, ping, coordinates and clicks-per-second (CPS) in the top-left corner. All lines toggleable via config.",
        "body": "## PvP HUD\n\nA clean client-side HUD for Minecraft PvP, shown in the top-left corner:\n\n- **FPS** — current frame rate\n- **Ping** — latency to the current server\n- **Coordinates** — XYZ position\n- **CPS** — left / right clicks per second (sliding 1-second window)\n\nEvery line can be toggled in `config/pvphud.json` (generated on first launch).\n\n## Install\n\nRequires **Fabric Loader** and **Fabric API** for Minecraft 1.21.4.\n\nDrop the jar into `.minecraft/mods/`.\n\n## Config\n\n| Key | Default | Meaning |\n|---|---|---|\n| `hudEnabled` | true | Enable the HUD |\n| `hudShowFps` | true | FPS line |\n| `hudShowPing` | true | Ping line |\n| `hudShowCoords` | true | Coordinates line |\n| `hudShowCps` | true | CPS line |\n| `hudShadow` | true | Text shadow |\n",
        "file": os.path.join(REPO, "mods/pvphud/build/libs/pvphud-1.1.0.jar"),
        "version": "1.1.0",
    },
    {
        "slug": "fliflight-custom-crosshair",
        "title": "Custom Crosshair",
        "description": "Customizable client-side crosshair for Minecraft PvP: 5 shapes, colors, size, presets — all editable in-game (default key: C).",
        "body": "## Custom Crosshair\n\nReplace the vanilla crosshair with a fully customizable one, straight from an in-game menu — no resource packs needed.\n\n- **5 shapes**: cross, dot, x, circle, t\n- **Color**: 8 presets + RGB sliders\n- **Size / thickness / center gap** sliders\n- **6 ready-made presets**: Classic Cross, Dot, X, Circle, T, Valorant\n- **Live preview** in the settings screen\n\n## Usage\n\nPress **C** in-game (rebindable in Options → Controls) to open the settings screen. Every change applies instantly and saves to `config/custom-crosshair.json`.\n\n## Install\n\nRequires **Fabric Loader** and **Fabric API** for Minecraft 1.21.4.\n\nDrop the jar into `.minecraft/mods/`.\n",
        "file": os.path.join(REPO, "mods/custom-crosshair/build/libs/custom-crosshair-1.1.0.jar"),
        "version": "1.1.0",
    },
]

def multipart_post(url, data_json, file_field=None, file_path=None):
    boundary = "----fliflightmirrorboundary"
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

for m in MODS:
    print(f"\n########## {m['title']} ##########")
    # 1. Create project (draft)
    proj = {
        "slug": m["slug"],
        "title": m["title"],
        "description": m["description"],
        "body": m["body"],
        "categories": ["utility"],
        "client_side": "required",
        "server_side": "unsupported",
        "project_type": "mod",
        "license_id": "LicenseRef-All-Rights-Reserved",
        "is_draft": True,
        "initial_versions": [],
        "loaders": ["fabric"],
    }
    status, body = multipart_post(f"{BASE}/project", proj)
    print("POST /project ->", status)
    try:
        pid = json.loads(body)["id"]
    except Exception:
        print("  BODY:", body[:400])
        continue
    print("  project_id =", pid)

    # 2. Upload version
    ver = {
        "project_id": pid,
        "name": f"{m['title']} {m['version']}",
        "version_number": m["version"],
        "changelog": "Initial release.",
        "dependencies": [
            {"version_id": None, "project_id": FABRIC_API_ID, "dependency_type": "required"}
        ],
        "game_versions": ["1.21.4"],
        "version_type": "release",
        "loaders": ["fabric"],
        "featured": False,
        "file_parts": [os.path.basename(m["file"])],
        "primary_file": os.path.basename(m["file"]),
    }
    status, body = multipart_post(f"{BASE}/version", ver, file_field=os.path.basename(m["file"]), file_path=m["file"])
    print("POST /version ->", status)
    if status >= 400:
        print("  BODY:", body[:500])
        continue
    print("  version uploadée")

    # 3. Submit for review
    req = urllib.request.Request(f"{BASE}/project/{pid}", data=json.dumps({"status": "processing"}).encode(), method="PATCH")
    req.add_header("Authorization", MR_TOKEN)
    req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req)
        print("PATCH status processing ->", resp.status)
    except urllib.error.HTTPError as e:
        print("PATCH ->", e.code, e.read().decode()[:200])

    print("  SLUG:", m["slug"])
