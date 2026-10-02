# Bedrock — `.mcpack` + dépôt MCPEDL

## Fichiers générés (`dist/bedrock/`, 7 packs vérifiés)

| Pack | Fichier | Note |
|---|---|---|
| Clear Lava | `fliflight-clear-lava.mcpack` | animé (flipbook) |
| Clear Pumpkin | `fliflight-clear-pumpkin.mcpack` | — |
| Clear Spyglass | `fliflight-clear-spyglass.mcpack` | → `textures/entity/spyglass.png` |
| Low Fire | `fliflight-low-fire.mcpack` | animé (flipbook) |
| Thin Totem | `fliflight-thin-totem.mcpack` | → `textures/items/totem.png` |
| Short Sword | `pvp-sword-little-sword-all-versions.mcpack` | — |
| Visible Ores | `visible-ores-all-versions-and-netherite.mcpack` | deepslate → sous-dossier |

Chemins **vérifiés contre `Mojang/bedrock-samples`** (resource pack vanilla officiel).

**Exclus (14)** :
- **7 crosshairs + `clean-hotbar` + `pvp-essentials`** → textures HUD/gui (pas d'équivalent Bedrock).
- **`clear-water`, `no-vignette`, `clear-powder-snow`** → textures `underwater`/`vignette`/`powder_snow_outline` **absentes de Bedrock** (gérées par le moteur, non remplaçables).
- **`low-shield`** → modèle 3D Java (aucune texture).
- **mod Diamonds** → mod Java NeoForge.

Régénérer : `python3 scripts/build_all_mcpacks.py`

## ✅ Chemins vérifiés (source officielle)
Vérifiés contre `Mojang/bedrock-samples` :
- minerais deepslate → `textures/blocks/deepslate/`
- totem → `textures/items/totem.png` · spyglass → `textures/entity/spyglass.png`
- animations lave/feu → `textures/flipbook_textures.json` (converti depuis les `.mcmeta` Java)

Il reste juste à **importer un `.mcpack` dans Bedrock** pour confirmer visuellement.

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
| Clear Lava | `Clear Lava — See Through Lava` | Reduced lava opacity so you can see what's below |
| Clear Pumpkin | `Clear Pumpkin — No Pumpkin Blur` | No more pumpkin overlay blocking your view |
| Clear Spyglass | `Clear Spyglass — Full Screen Scope` | Cleaner spyglass view with no dark border |
| Low Fire | `Low Fire — Lowered Flame` | Lower fire so it never blocks your screen in fights |
| Thin Totem | `Thin Totem — Smaller Totem Pop` | A smaller, less obtrusive totem pop animation |
| Short Sword | `Short Sword — Smaller Swords` | Compact swords for better PvP visibility |
| Visible Ores | `Visible Ores — See Every Ore` | Ores and netherite stand out clearly (shader friendly) |

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
