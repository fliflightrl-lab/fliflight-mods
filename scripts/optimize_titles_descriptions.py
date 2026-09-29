#!/usr/bin/env python3
"""Rewrite titles / summaries / descriptions to match CurseForge's stated rules
(Moderation Policies + Project Submission Guide) and push them to Modrinth.

CF rules applied:
  - Name: short, unique, English, no game name / version / category words.
  - Summary: ONE line, what it does (not who it's for), no generic filler, not a copy of the body.
  - Description: states what it changes, functional info, install steps, supported versions;
    promo / donation links go at the BOTTOM.
  - A sample image is mandatory for resource packs (2 titled images + featured now exist).
"""
import json, os
import requests

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")
CRED = json.load(open(r"C:\Users\user\.config\fliflightmc\credentials.json"))
HDR = {"Authorization": CRED["modrinth"]["token"], "User-Agent": "fliflightmc/1.0"}
API = "https://api.modrinth.com/v2"

CF_FLAGSHIP = "https://www.curseforge.com/minecraft/texture-packs/pvp-essentials-crosshair-visible-ores-sword-low"
KOFI = "https://ko-fi.com/fliflight"

# slug -> (local dir, modrinth id, cf slug, title, summary, what-changes bullets, why bullets)
DATA = {
    "fliflight-low-shield": (
        "fliflight-low-shield", "3kHplXd9", "low-shield-shield-out-of-the-way",
        "Low Shield - See Past Your Shield",
        "Shrinks and lowers the first-person shield so it stops covering your screen in fights.",
        ["The held shield renders about 45% smaller in first person",
         "It also sits lower, below your crosshair instead of across the middle of the screen",
         "Blocking still works exactly like vanilla - only the visuals change"],
        ["You keep your target, the mob in front of you and your surroundings visible while blocking",
         "Useful in PvP, in raids and against any mob that makes you hold right-click"],
    ),
    "fliflight-no-vignette": (
        "fliflight-no-vignette", "JYyEzln5", "no-vignette-clear-screen-corners",
        "No Vignette - Brighter Screen, No Dark Corners",
        "Removes the dark corner shading so the whole screen stays evenly lit, day and night.",
        ["The vignette overlay is replaced with a flat one, so no corner is darkened",
         "Nothing else is touched - the rest of the HUD stays vanilla"],
        ["Easier to spot movement at the edges of your screen in a cave or at night",
         "The screen looks brighter without changing your brightness or gamma"],
    ),
    "fliflight-clear-water": (
        "fliflight-clear-water", "4KyMcPC1", "clear-water-see-through-water",
        "Clear Water - See Through Water",
        "Makes water translucent so you can see the seabed, ores and mobs while swimming.",
        ["Water is rendered translucent instead of opaque",
         "The full-screen blue overlay you get with your head underwater is removed",
         "The water surface overlay is cleared as well, so the view stays clean from above too"],
        ["You can spot mineshafts, shipwrecks, mobs and ore while swimming",
         "Handy for ocean monuments, drowned farming and underwater building"],
    ),
    "fliflight-clear-lava": (
        "fliflight-clear-lava", "eG9N5405", "clear-lava-see-through-lava",
        "Clear Lava - See Through Lava",
        "Makes lava semi-transparent so you can see the terrain underneath before you jump in.",
        ["Lava is rendered semi-transparent instead of solid orange",
         "Both the still and the flowing texture are changed, so the effect is consistent",
         "The lava still looks like lava - it just no longer hides what is below"],
        ["You can see where the ground is before crossing a lava lake in the Nether",
         "Useful for mining around lava and for spotting mobs or items under the surface"],
    ),
    "fliflight-clear-spyglass": (
        "fliflight-clear-spyglass", "HEAEl6k5", "clear-spyglass-no-scope-overlay",
        "Clear Spyglass - Full Screen Zoom",
        "Removes the spyglass scope overlay so the full screen stays usable while you zoom.",
        ["The black scope circle and its border are removed from the spyglass view",
         "Zoom behaviour is untouched - only the overlay texture changes"],
        ["You keep full peripheral vision while scouting, so you are not blind while zoomed",
         "Great for spotting players, bases and terrain from far away"],
    ),
    "fliflight-clean-hotbar": (
        "fliflight-clean-hotbar", "PDnvunp5", "clean-hotbar-flat-minimal-hud",
        "Clean Hotbar - Flat Minimal HUD",
        "Replaces the vanilla hotbar and XP bar with a flat design that is easier to read at a glance.",
        ["The hotbar is redrawn as flat dark slots with a thin outline - all 9 slots kept",
         "The slot selector is a clean white frame instead of the vanilla arrow marker",
         "The XP bar gets a dark track and a bright green fill"],
        ["Less visual noise on the bottom of your screen while keeping every vanilla function",
         "Easier to read your XP level and your items quickly during a fight"],
    ),
    "fliflight-thin-totem": (
        "fliflight-thin-totem", "32hlofGi", "thin-totem-slimmer-totem-pop",
        "Thin Totem - Smaller Totem Pop",
        "Slims the totem of undying so its pop animation stops blocking your view mid-fight.",
        ["The totem art is redrawn narrower and centred on the same 16x16 canvas",
         "The item model and animation are untouched, so it behaves exactly like vanilla"],
        ["When a totem pops in a fight you keep sight of your opponent instead of a wall of gold",
         "Also takes less space in your inventory icon and in your off-hand"],
    ),
    "fliflight-clear-powder-snow": (
        "fliflight-clear-powder-snow", "fQlGVRS8", "clear-powder-snow-no-frost-overlay",
        "Clear Powder Snow - No Freeze Overlay",
        "Removes the frost overlay so you can still see where you are going while freezing.",
        ["The frost / ice overlay drawn around the edges of the screen is removed",
         "Nothing else changes - freezing, damage and the slow effect all work as in vanilla"],
        ["You can find the way out of powder snow instead of being blinded by frost",
         "Handy in snowy biomes and for exploring mountains"],
    ),
    "fliflight-clear-pumpkin": (
        "fliflight-clear-pumpkin", "xnQODGjN", "clear-pumpkin-no-pumpkin-blur",
        "Clear Pumpkin - No Pumpkin Blur",
        "Removes the orange pumpkin blur overlay so you can see clearly while wearing a pumpkin.",
        ["The pumpkin blur overlay (pumpkinblur) is replaced with a fully transparent texture",
         "Wearing a pumpkin still works normally - you only lose the orange veil"],
        ["The classic Enderman trick becomes actually playable, you can see where you walk",
         "Useful for survival, mob farms and for the End"],
    ),
    "fliflight-pvp-essentials": (
        "pvp-essentials", "cHpwGcrb", "pvp-essentials-crosshair-visible-ores-sword-low",
        "PvP Essentials",
        "One pack for PvP: a clean dot crosshair, visible ores, smaller swords, low fire and a clear pumpkin.",
        ["A clean 1px dot crosshair (replaces the vanilla crosshair)",
         "Visible ores - every ore and ancient debris stands out",
         "Smaller swords, so your weapon stops covering the middle of the screen",
         "Low fire - the flame sits lower with the full animation, in the world and in the GUI",
         "Clear pumpkin - no orange blur when wearing one"],
        ["Everything above comes from five separate packs and is bundled here so you install it once",
         "Each feature keeps working like its original pack, this is just the all-in-one convenience build"],
    ),
}


def build_md_body(title, bullets_change, bullets_why):
    lines = [f"**{title}** is a client-side resource pack for Minecraft Java Edition. "
             f"It changes one specific thing about the vanilla look, and nothing else.", ""]
    lines.append("### What it changes")
    lines += [f"- {b}" for b in bullets_change]
    lines.append("")
    lines.append("### Why players use it")
    lines += [f"- {b}" for b in bullets_why]
    lines.append("")
    lines.append("### Install")
    lines.append("1. Download the `.zip` file from this page (do not unzip it).")
    lines.append("2. Drop it into `.minecraft/resourcepacks` - or use the CurseForge app.")
    lines.append("3. Enable it in **Options → Resource Packs** and move it to the top of the list.")
    lines.append("")
    lines.append("Works on Minecraft **1.21.x** (Java Edition) and on most launchers. "
                 "Client-side only: it works on any server, and no one else needs it.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### Get the whole set")
    lines.append(f"This is part of the **PvP Essentials** family - the all-in-one pack with crosshair, "
                 f"visible ores, short sword, low fire and clear pumpkin: [PvP Essentials]({CF_FLAGSHIP})")
    lines.append("")
    lines.append(f"Liked it? You can support the work on [Ko-fi]({KOFI}).")
    return "\n".join(lines)


def build_html_body(md):
    """markdown-ish -> simple HTML for the CurseForge description field."""
    import re
    out = []
    for raw in md.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
            continue
        if line.strip() == "---":
            out.append("<hr>")
            continue
        if line.startswith("- "):
            out.append(f"<p>• {line[2:]}</p>")
            continue
        if re.match(r"^\d+\. ", line):
            out.append(f"<p>{line}</p>")
            continue
        out.append(f"<p>{line}</p>")
    html = "".join(out)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)
    html = html.replace("`", "")
    return html


cf_payload = {}
for slug, (folder, pid, cfslug, title, summary, bch, bwh) in DATA.items():
    md = build_md_body(title, bch, bwh)
    path = os.path.join(PACKS, folder, "manifest.json")
    m = json.load(open(path, encoding="utf-8"))

    # CF wants the name without the em-dash subtitle where it would be "excessive" -> keep, it is functional
    m["name"] = title
    m["summary"] = summary
    m["body"] = md.replace("\n", "\\n")
    json.dump(m, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"[{slug}] manifest updated: {title!r}")

    # push to Modrinth (title must stay short there: strip the subtitle for Modrinth)
    mr_title = title.split(" - ")[0] if slug != "fliflight-pvp-essentials" else title
    r = requests.patch(f"{API}/project/{pid}", headers=HDR,
                       json={"title": mr_title, "description": summary, "body": md})
    print(f"    modrinth: title={mr_title!r} -> {r.status_code}")

    cf_payload[slug] = {
        "cf_id": m.get("curseforge_id"), "cf_slug": cfslug,
        "name": title, "summary": summary,
        "description_html": build_html_body(md),
        "changelog": m["version"]["changelog"],
        "game_versions": m["version"]["game_versions"],
        "logo": f"dist/cf_logos/{slug}-512.png",
        "gallery": [f"packs/{folder}/gallery/{g}" for g in sorted(os.listdir(os.path.join(PACKS, folder, "gallery"))) if g.endswith(".png")],
    }

out = os.path.join(BASE, "cf_payload.json")
json.dump(cf_payload, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nwrote", out)
