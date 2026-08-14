#!/usr/bin/env python3
"""
Unified publisher — one command pushes a pack to every platform.

Targets:
  modrinth   create a new version on the existing Modrinth project
  curseforge upload a new file to the existing CurseForge project
  github     create a GitHub Release (tag + asset)
  pmc        generate a Planet Minecraft upload kit (no public API — manual step)

Usage:
  python3 publish.py --pack <slug> [--targets modrinth,curseforge,github,pmc] [--dry-run]
  python3 publish.py --all --targets pmc
  python3 publish.py --verify          # read-only consistency check (safe)

Credentials are read from env vars first, then ~/.config/fliflightmc/credentials.json:
  CF_API_KEY, MR_TOKEN, GH_TOKEN, GH_REPO ("owner/repo").
"""
import argparse, json, os, sys, shutil

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
PACKS = os.path.join(ROOT, "packs")
CREDS_FILE = os.path.expanduser("~/.config/fliflightmc/credentials.json")

MODRINTH_API = "https://api.modrinth.com/v2"
CF_UPLOAD_API = "https://minecraft.curseforge.com/api"
GITHUB_API = "https://api.github.com"

LICENSE_REF = "LicenseRef-All-Rights-Reserved"
RELEASE_TYPE = {"release": "release", "beta": "beta", "alpha": "alpha"}


def load_credentials():
    creds = {}
    if os.path.exists(CREDS_FILE):
        raw = json.load(open(CREDS_FILE, encoding="utf-8"))
        creds["CF_API_KEY"] = raw.get("curseforge", {}).get("api_key")
        creds["MR_TOKEN"] = raw.get("modrinth", {}).get("token")
    for k in ("CF_API_KEY", "MR_TOKEN", "GH_TOKEN", "GH_REPO"):
        if os.environ.get(k):
            creds[k] = os.environ[k]
    return creds


def load_manifest(slug):
    p = os.path.join(PACKS, slug, "manifest.json")
    if not os.path.exists(p):
        raise SystemExit(f"No pack '{slug}' (looked for {p})")
    return json.load(open(p, encoding="utf-8"))


def list_packs():
    return sorted(d for d in os.listdir(PACKS)
                  if os.path.exists(os.path.join(PACKS, d, "manifest.json")))


def file_path(m):
    return os.path.join(PACKS, m["slug"], "files", m["file"])


# --------------------------------------------------------------------------- #
# Modrinth
# --------------------------------------------------------------------------- #
def modrinth_publish(m, token, dry_run):
    v = m["version"]
    data = {
        "project_id": m["modrinth_id"],
        "name": v["number"],
        "version_number": v["number"],
        "changelog": v.get("changelog", ""),
        "dependencies": [],
        "game_versions": v["game_versions"],
        "version_type": v["type"],
        "loaders": v["loaders"],
        "featured": False,
        "file_parts": [m["file"]],
        "primary_file": m["file"],
    }
    # NOTE: `environment` omitted — `minecraft` loader doesn't support it (see skill).
    fp = file_path(m)
    size = os.path.getsize(fp)
    print(f"[modrinth] project={m['modrinth_id']} version={v['number']} "
          f"loaders={v['loaders']} file={m['file']} ({size} B)")
    if dry_run:
        print("[modrinth] DRY-RUN: would POST /version")
        return
    with open(fp, "rb") as f:
        files = {
            "data": (None, json.dumps(data), "application/json"),
            m["file"]: (m["file"], f.read(), "application/octet-stream"),
        }
        r = requests.post(f"{MODRINTH_API}/version",
                          headers={"Authorization": token}, files=files, timeout=180)
    if r.status_code in (200, 201):
        print(f"[modrinth] OK -> version id={r.json().get('id')}")
    else:
        print(f"[modrinth] ERROR {r.status_code}: {r.text[:400]}")
        raise SystemExit(1)


# --------------------------------------------------------------------------- #
# CurseForge
# --------------------------------------------------------------------------- #
_cf_game_versions = None


def cf_resolve_game_versions(token, game_versions):
    """Resolve Minecraft version names -> CF game-version ids via the READ api
    (api.curseforge.com), which accepts the bcrypt key. The UPLOAD api
    (minecraft.curseforge.com/api) rejects it as 'malformed', so we resolve ids
    on the side that works."""
    global _cf_game_versions
    if _cf_game_versions is None:
        h = {"x-api-key": token}
        r = requests.get("https://api.curseforge.com/v1/minecraft/version", headers=h, timeout=60)
        if r.status_code != 200:
            raise SystemExit(f"[curseforge] /v1/minecraft/version -> {r.status_code}: {r.text[:200]}")
        _cf_game_versions = {str(v.get("versionString")): v.get("gameVersionId")
                             for v in r.json().get("data", []) if v.get("versionString")}
    ids, missing = [], []
    for gv in game_versions:
        if gv in _cf_game_versions:
            ids.append(_cf_game_versions[gv])
        else:
            missing.append(gv)
    return sorted(set(i for i in ids if i)), missing


def curseforge_publish(m, token, dry_run):
    v = m["version"]
    print(f"[curseforge] project={m['curseforge_id']} version={v['number']} "
          f"loaders={v['loaders']} game_versions={len(v['game_versions'])}")
    ids, missing = cf_resolve_game_versions(token, v["game_versions"])
    if missing:
        print(f"[curseforge] WARN: {len(missing)} game versions not found in CF map: "
              f"{missing[:10]}{'...' if len(missing) > 10 else ''}")
    if not ids:
        raise SystemExit("[curseforge] no resolvable game version ids — aborting (safe)")
    metadata = {
        "changelog": v.get("changelog", ""),
        "changelogType": "markdown",
        "displayName": v["number"],
        "gameVersions": ids,
        "releaseType": RELEASE_TYPE.get(v["type"], "release"),
    }
    fp = file_path(m)
    print(f"[curseforge] resolved {len(ids)} game-version ids, file={m['file']} ({os.path.getsize(fp)} B)")
    if dry_run:
        print(f"[curseforge] DRY-RUN: would POST /projects/{m['curseforge_id']}/upload-file")
        return
    with open(fp, "rb") as f:
        files = {
            "file": (m["file"], f.read(), "application/octet-stream"),
            "metadata": (None, json.dumps(metadata), "application/json"),
        }
        r = requests.post(f"{CF_UPLOAD_API}/projects/{m['curseforge_id']}/upload-file",
                          headers={"X-Api-Token": token}, files=files, timeout=300)
    if r.status_code in (200, 201):
        j = r.json()
        print(f"[curseforge] OK -> file id={j.get('id')}")
    else:
        txt = r.text[:400]
        print(f"[curseforge] ERROR {r.status_code}: {txt}")
        if "malformed" in txt:
            print("[curseforge] -> This CF key is accepted by the READ api (api.curseforge.com) but "
                  "rejected by the UPLOAD api (minecraft.curseforge.com/api). Generate a new/upload-capable "
                  "token at console.curseforge.com, or keep uploading to CurseForge via the website and "
                  "use the mirror direction (CF -> Modrinth/GitHub/PMC) instead.")
        raise SystemExit(1)


# --------------------------------------------------------------------------- #
# GitHub Releases
# --------------------------------------------------------------------------- #
def github_publish(m, token, repo, dry_run):
    v = m["version"]
    tag = f"{m['slug']}-{v['number']}"
    name = f"{m['name']} {v['number']}"
    body_lines = [m.get("summary", "").strip()]
    cf = (m.get("links") or {}).get("website_url")
    if cf:
        body_lines.append("")
        body_lines.append(f"CurseForge : {cf}")
    body_lines.append(f"Modrinth : https://modrinth.com/project/{m['slug']}")
    if v.get("changelog"):
        body_lines.append("")
        body_lines.append("## Changelog")
        body_lines.append(v["changelog"])
    body = "\n".join(body_lines)
    fp = file_path(m)
    print(f"[github] repo={repo} tag={tag} file={m['file']} ({os.path.getsize(fp)} B)")
    if dry_run:
        print("[github] DRY-RUN: would create release + upload asset")
        return
    h = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
    # get-or-create release
    r = requests.get(f"{GITHUB_API}/repos/{repo}/releases/tags/{tag}", headers=h, timeout=60)
    if r.status_code == 200:
        release = r.json()
        print(f"[github] release exists id={release['id']}")
    elif r.status_code == 404:
        r = requests.post(f"{GITHUB_API}/repos/{repo}/releases", headers=h, timeout=60,
                          json={"tag_name": tag, "name": name, "body": body, "draft": False})
        if r.status_code not in (200, 201):
            print(f"[github] create release ERROR {r.status_code}: {r.text[:300]}")
            raise SystemExit(1)
        release = r.json()
        print(f"[github] created release id={release['id']}")
    else:
        print(f"[github] get release ERROR {r.status_code}: {r.text[:300]}")
        raise SystemExit(1)
    # upload asset
    up_h = {"Authorization": f"token {token}", "Content-Type": "application/octet-stream",
            "Accept": "application/vnd.github+json"}
    url = f"https://uploads.github.com/repos/{repo}/releases/{release['id']}/assets?name={m['file']}"
    with open(fp, "rb") as f:
        r = requests.post(url, headers=up_h, data=f.read(), timeout=300)
    if r.status_code in (200, 201):
        print(f"[github] OK -> asset {r.json().get('browser_download_url')}")
    else:
        print(f"[github] upload asset ERROR {r.status_code}: {r.text[:300]}")
        raise SystemExit(1)


# --------------------------------------------------------------------------- #
# Planet Minecraft kit
# --------------------------------------------------------------------------- #
def pmc_kit(m, dry_run):
    v = m["version"]
    slug = m["slug"]
    kit = os.path.join(ROOT, "dist", "pmc", slug)
    shutil.rmtree(kit, ignore_errors=True)
    os.makedirs(kit)
    shutil.copy(file_path(m), os.path.join(kit, m["file"]))
    if m.get("icon"):
        shutil.copy(os.path.join(PACKS, slug, m["icon"]), kit)
    for g in m.get("gallery", []):
        shutil.copy(os.path.join(PACKS, slug, "gallery", g), kit)
    md = []
    md.append(f"# Upload kit: {m['name']}")
    md.append("")
    md.append("Planet Minecraft n'a pas d'API d'upload publique — dépôt manuel (~2 min).")
    md.append("")
    md.append("1. Va sur https://www.planetminecraft.com/account/manage/ et connecte-toi.")
    md.append("2. Bouton **Submit** → choisis le type: **Texture Pack** ou **Data Pack / Mod**.")
    md.append(f"3. Titre : `{m['name']}`")
    md.append(f"4. Résumé : `{m['summary']}`")
    md.append("5. Description (copier/coller) :")
    md.append("```")
    md.append(m.get("body", ""))
    md.append("```")
    cats = ", ".join(m.get("categories", []))
    md.append(f"6. Catégories/tags suggérés : `{cats}`")
    md.append(f"7. Game versions : `{', '.join(v['game_versions'][:6])}…` (ou 'toutes')")
    md.append(f"8. Fichier : `{m['file']}` (déjà dans ce dossier)")
    if m.get("icon"):
        md.append(f"9. Icône : `{m['icon']}` ; Galerie : {', '.join(m.get('gallery', [])) or '—'}")
    md.append(f"10. Changelog : `{v.get('changelog', '')}`")
    md.append("")
    md.append("> Le nom d'utilisateur PMC doit être le même (Fliflightmc) pour la cohérence SEO.")
    open(os.path.join(kit, "UPLOAD.md"), "w", encoding="utf-8").write("\n".join(md))
    print(f"[pmc] kit written to {kit}")


# --------------------------------------------------------------------------- #
# Verify (read-only)
# --------------------------------------------------------------------------- #
def verify(creds):
    mr = creds.get("MR_TOKEN")
    print("=== packs ===")
    for slug in list_packs():
        m = load_manifest(slug)
        fp = file_path(m)
        ok = "OK" if os.path.exists(fp) else "MISSING"
        print(f"  {slug:48} {m['project_type']:12} cf={m['curseforge_id']} mr={m['modrinth_id']} file[{ok}]")
    if mr:
        r = requests.get(f"{MODRINTH_API}/user", headers={"Authorization": mr}, timeout=30)
        if r.status_code == 200:
            uid = r.json().get("id")
            r2 = requests.get(f"{MODRINTH_API}/user/{uid}/projects",
                              headers={"Authorization": mr}, timeout=30)
            print("\n=== modrinth projects ===")
            for p in r2.json():
                print(f"  {p['id']}  {p['status']:12} {p['project_type']:14} {p['slug']}")
        else:
            print(f"\n[verify] modrinth user check failed: {r.status_code}")
    cf = creds.get("CF_API_KEY")
    if cf:
        r = requests.get("https://api.curseforge.com/v1/games", headers={"x-api-key": cf}, timeout=30)
        print(f"\n[verify] curseforge read-api status: {r.status_code}")
        ids, missing = cf_resolve_game_versions(cf, ["1.21.4", "1.21.8", "26.2"])
        print(f"[verify] curseforge game-version resolve sample: {len(ids)} resolved, missing={missing}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", help="pack slug")
    ap.add_argument("--all", action="store_true", help="operate on all packs")
    ap.add_argument("--targets", default="modrinth,curseforge,github,pmc",
                    help="comma list: modrinth,curseforge,github,pmc")
    ap.add_argument("--dry-run", action="store_true", help="print actions, no side effects")
    ap.add_argument("--verify", action="store_true", help="read-only consistency check")
    args = ap.parse_args()

    creds = load_credentials()
    targets = [t.strip() for t in args.targets.split(",") if t.strip()]

    if args.verify:
        verify(creds)
        return

    slugs = list_packs() if args.all else [args.pack]
    if not slugs or not slugs[0]:
        raise SystemExit("Pass --pack <slug> or --all")
    for slug in slugs:
        m = load_manifest(slug)
        print(f"\n===== {slug} ({m['project_type']}) =====")
        if "modrinth" in targets:
            if not creds.get("MR_TOKEN"):
                print("[modrinth] SKIP — no MR_TOKEN")
            else:
                modrinth_publish(m, creds["MR_TOKEN"], args.dry_run)
        if "curseforge" in targets:
            if not creds.get("CF_API_KEY"):
                print("[curseforge] SKIP — no CF_API_KEY")
            else:
                curseforge_publish(m, creds["CF_API_KEY"], args.dry_run)
        if "github" in targets:
            if not (creds.get("GH_TOKEN") and creds.get("GH_REPO")):
                print("[github] SKIP — no GH_TOKEN/GH_REPO")
            else:
                github_publish(m, creds["GH_TOKEN"], creds["GH_REPO"], args.dry_run)
        if "pmc" in targets:
            pmc_kit(m, args.dry_run)


if __name__ == "__main__":
    main()
