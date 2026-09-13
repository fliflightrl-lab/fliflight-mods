#!/usr/bin/env python3
"""Crée les 21 posts restants sur Buffer (YouTube + TikTok), planning étalé."""
import json, os, urllib.request, time

creds = json.load(open(os.path.expanduser("~/.config/fliflightmc/credentials.json")))
b = creds["buffer"]
TOKEN, URL = b["token"], b["graphql_endpoint"]

YT = "6a7f5d27b2d9d5774379e036"   # YouTube "noxe"
TT = "6a7f6079b2d9d577437a0f78"   # TikTok "fliflight"

MUT = """
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    __typename
    ... on PostActionSuccess { post { id dueAt } }
    ... on InvalidInputError { message }
    ... on LimitReachedError { message }
    ... on UnexpectedError { message }
    ... on RestProxyError { message }
    ... on NotFoundError { message }
    ... on UnauthorizedError { message }
  }
}
"""

def gql(query, variables=None):
    body = {"query": query}
    if variables: body["variables"] = variables
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"http_error": e.code, "body": e.read().decode()[:1500]}

BASE_URL = "https://github.com/fliflightrl-lab/fliflight-mods/releases/download/shorts-pvp-batch1"

HOOKS = {1:"CE COMBAT ÉTAIT CHAUD", 2:"IL PENSAIT GAGNER", 3:"TROP RAPIDE POUR LUI",
         4:"LE DERNIER COUP", 5:"POV : TU CLUTCH", 6:"IL A RIEN PU FAIRE",
         8:"INARRÊTABLE", 9:"LA PRESSION MONTE", 10:"ELLE EST POUR TOI",
         11:"UN SHOT, UN KILL", 12:"ET BOOM."}

TITLES = {1:"CE 1v1 ÉTAIT CHAUD 🔥 (Minecraft PvP)",
          2:"IL PENSAIT GAGNER... (Minecraft PvP Clutch)",
          3:"TROP RAPIDE POUR LUI ⚡ (Minecraft PvP)",
          4:"LE DERNIER COUP 🎯 (Minecraft PvP)",
          5:"POV : TU CLUTCH EN 1v1 💪 (Minecraft PvP)",
          6:"IL A RIEN PU FAIRE 😤 (Minecraft PvP)",
          8:"INARRÊTABLE 🔥 (Minecraft PvP)",
          9:"LA PRESSION MONTE 📈 (Minecraft PvP)",
          10:"ELLE EST POUR TOI CELLE-LÀ 😳 (Minecraft PvP)",
          11:"UN SHOT, UN KILL 🎯 (Minecraft PvP)",
          12:"ET BOOM. 💥 (Minecraft PvP)"}

# planning: (n, date, heure) — w01 YouTube déjà fait
SCHEDULE = [
    (1,  "2026-09-14", "18:00"),
    (2,  "2026-09-14", "20:00"),
    (3,  "2026-09-15", "18:00"),
    (4,  "2026-09-16", "18:00"),
    (5,  "2026-09-17", "18:00"),
    (6,  "2026-09-18", "18:00"),
    (8,  "2026-09-19", "18:00"),
    (9,  "2026-09-20", "18:00"),
    (10, "2026-09-21", "18:00"),
    (11, "2026-09-22", "18:00"),
    (12, "2026-09-23", "18:00"),
]

def desc(n):
    return (f"🔥 {HOOKS[n]} — clutch Minecraft PvP !\n\n"
            "⚔️ Crosshair custom, ores visibles, épées courtes… tous mes packs sont GRATUITS "
            "👉 https://linktr.ee/fliflight\n"
            "💬 Discord, réseaux & tout le reste : même lien en bio\n\n"
            "Abonne-toi pour plus de PvP 🔥\n\n"
            "#minecraft #minecraftpvp #pvp #shorts #gaming #crosshair #fyp")

def make(n, ch, due):
    vid = f"{BASE_URL}/final_w{n:02d}.mp4"
    title = TITLES[n]
    inp = {
        "channelId": ch,
        "text": desc(n),
        "assets": [{"video": {"url": vid, "metadata": {"title": title}}}],
        "mode": "customScheduled",
        "schedulingType": "automatic",
        "needsApproval": False,
        "dueAt": due,
    }
    if ch == YT:
        inp["metadata"] = {"youtube": {"title": title, "privacy": "public",
                                       "madeForKids": False, "categoryId": "20",
                                       "notifySubscribers": True, "isAiGenerated": False}}
    else:
        inp["metadata"] = {"tiktok": {"title": title, "isAiGenerated": False}}
    return gql(MUT, {"input": inp})

ok, fail = 0, 0
for n, date, hm in SCHEDULE:
    due = f"{date}T{hm}:00+02:00"
    channels = [TT] if n == 1 else [YT, TT]   # w01 YouTube déjà créé
    for ch in channels:
        r = make(n, ch, due)
        res = r.get("data", {}).get("createPost", {})
        tn = res.get("__typename")
        label = "YouTube" if ch == YT else "TikTok"
        if tn == "PostActionSuccess":
            ok += 1
            print(f"OK   w{n:02d} {label:8s} {date} {hm} -> {res['post']['id']}")
        else:
            fail += 1
            print(f"FAIL w{n:02d} {label:8s} {date} {hm} -> {tn}: {res.get('message') or r.get('body','')[:200]}")
        time.sleep(1)

print(f"\nRESULTAT: {ok} créés, {fail} échecs")
