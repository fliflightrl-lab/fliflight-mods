# Bedrock — `.mcpack` + dépôt MCPEDL

## Fichiers générés (`dist/bedrock/`, 10 packs portables)

| Pack | Fichier |
|---|---|
| Clear Water | `fliflight-clear-water.mcpack` |
| Clear Lava | `fliflight-clear-lava.mcpack` |
| Clear Pumpkin | `fliflight-clear-pumpkin.mcpack` |
| Clear Spyglass | `fliflight-clear-spyglass.mcpack` |
| Clear Powder Snow | `fliflight-clear-powder-snow.mcpack` |
| Low Fire | `fliflight-low-fire.mcpack` |
| No Dark Corners | `fliflight-no-vignette.mcpack` |
| Thin Totem | `fliflight-thin-totem.mcpack` |
| Short Sword | `pvp-sword-little-sword-all-versions.mcpack` |
| Visible Ores | `visible-ores-all-versions-and-netherite.mcpack` |

**Exclus (Java-only)** : les 7 crosshairs + `clean-hotbar` (textures HUD crosshair) + `low-shield` (modèle 3D, pas de texture) + `pvp-essentials` (bundle, contient le crosshair) + le mod Diamonds (Java NeoForge).
Régénérer : `python3 scripts/build_all_mcpacks.py`

## ⚠️ À vérifier avant publication
Les `.mcpack` sont générés par mapping automatique des chemins Java → Bedrock.
**Teste-les dans Bedrock** (Windows/Android) avant de publier : certains noms de textures
diffèrent parfois entre Java et Bedrock (ex. animés via `flipbook_textures.json` côté Bedrock).
Je ne peux pas exécuter Bedrock ici — c'est le seul point que je ne peux pas vérifier.

## Listing MCPEDL — modèle prêt à coller (EN)

**Title:** `{pack} — {tagline} for Bedrock`

**Description (modèle) :**
```
{Tagline}.

✅ Works on Bedrock (Windows, Android, iOS, consoles)
✅ No mods required — just import the .mcpack
✅ Lightweight and vanilla-friendly

How to install:
1. Download the .mcpack
2. Open it (double-click on Windows, or tap on mobile)
3. Minecraft imports it automatically — enable it in Settings → Global Resources

Enjoy! More PvP/utility packs: https://fliflightrl-lab.github.io/fliflight-mods/
```

## Titres + accroches suggérés

| Pack | Title | Tagline |
|---|---|---|
| Clear Water | `Clear Water — See Underwater` | See clearly underwater instead of the murky blue tint |
| Clear Lava | `Clear Lava — See Through Lava` | Reduced lava opacity so you can see what's below |
| Clear Pumpkin | `Clear Pumpkin — No Pumpkin Blur` | No more pumpkin overlay blocking your view |
| Clear Spyglass | `Clear Spyglass — Full Screen Scope` | Cleaner spyglass view with no dark border |
| Clear Powder Snow | `Clear Powder Snow — No Freeze Overlay` | Remove the powder snow freeze vignette |
| Low Fire | `Low Fire — Lowered Flame` | Lower fire so it never blocks your screen in fights |
| No Dark Corners | `No Dark Corners — Remove Vignette` | Removes the dark vignette around the screen edges |
| Thin Totem | `Thin Totem — Smaller Totem Pop` | A smaller, less obtrusive totem pop animation |
| Short Sword | `Short Sword — Smaller Swords` | Compact swords for better PvP visibility |
| Visible Ores | `Visible Ores — See Every Ore` | Ores and netherite stand out clearly (Optifine/shader friendly) |

**Tags MCPEDL :** PvP, Utility, GUI, Textures, 16x, Client-side

## Étapes de dépôt MCPEDL
1. Crée un compte sur https://mcpedl.com (gratuit).
2. **Submit** → choisis la catégorie (**Texture Packs** ou **Utility**).
3. Colle le titre + la description ci-dessus, upload l'icône `pack_icon` (déjà dans le `.mcpack`) + 2-3 images.
4. Upload le `.mcpack` ou héberge-le (lien vers ton site/GitHub).
5. Soumets — la modération MCPEDL valide en ~1-3 jours.

## Ensuite : Marketplace officiel
Une fois validé sur MCPEDL (preuve de qualité), candidate au **Marketplace** via
`partner.microsoft.com` → programme Minecraft Marketplace (voir `02-bedrock-portage.md`).
C'est le seul canal où un texture pack se **vend** (Minecoins → USD).
