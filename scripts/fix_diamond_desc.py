import json, requests
CRED = json.load(open(r'C:\Users\user\.config\fliflightmc\credentials.json'))
HDR = {'Authorization': CRED['modrinth']['token']}
API = 'https://api.modrinth.com/v2'

body = """Craft a special lighter from **9 diamond blocks + flint & steel**, then right-click to open a portal to the **Diamond Dimension** - an entire world built from solid diamond.

## What it adds
- A new dimension where the ground, mountains and caves are made of **diamond blocks**
- Rich ore veins - the deeper you go, the more valuable the terrain
- A return portal that brings you back to the Overworld

## Why play it?
- **End-game content**: a high-risk, high-reward world for players who have already found every diamond in the Overworld
- **Building paradise**: mine entire mountains of diamond blocks for your next mega-build
- **Exploration**: brand-new terrain generation to explore, with diamonds everywhere you look

## Requirements
- **NeoForge** (for Minecraft 1.21.4)

## Install
1. Install NeoForge for Minecraft 1.21.4
2. Drop the .jar file into your mods folder
3. Launch the game, craft the Diamond Lighter, and step through the portal

---

**Looking for a resource pack?** [Visible Ores](https://www.curseforge.com/minecraft/texture-packs/visible-ores-all-versions-and-netherite) - see every ore clearly."""

r = requests.patch(f'{API}/project/diamond-dimension', headers=HDR, json={'body': body})
print('diamond body re-updated:', r.status_code)

# verify
d = requests.get(f'{API}/project/diamond-dimension', headers=HDR).json()
print('body check:', d['body'][:120])
print('backtick corruption:', 'backtick' if 'Drop the  into' in d['body'] else 'clean')
