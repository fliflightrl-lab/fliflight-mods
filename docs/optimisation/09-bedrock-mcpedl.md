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

## Dépôt MCPEDL — ⚠️ plus de dépôt direct depuis le 30/04/2025
Il n'y a **plus de formulaire d'upload sur MCPEDL**. Tout se fait via **CurseForge**
(voir la section « Automatiser MCPEDL » ci-dessous). Le listing ci-dessus sert pour la
**description du projet CurseForge Bedrock**.

## 🤖 Automatiser MCPEDL (= automatiser CurseForge)

**Depuis le 30 avril 2025, MCPEDL n'accepte plus d'uploads directs.** Tout passe par la
**console d'auteur CurseForge**, et MCPEDL **synchronise automatiquement**. Donc :

> Tu automatises **CurseForge** → MCPEDL suit tout seul.

⚠️ Les projets concernés doivent être des projets **CurseForge « Minecraft Bedrock »**
(pas Java). Tes 19 projets CF actuels sont Java → il faut créer de **nouveaux projets
Bedrock** sur CF.

### Conditions du sync (toutes obligatoires)
1. **Connecter** ton compte CurseForge à ton profil MCPEDL : `mcpedl.com/dashboard/profile`
   → « Connected Accounts ».
2. Créer un projet CurseForge avec le jeu **« Minecraft Bedrock »**.
3. **Le slug doit être IDENTIQUE** sur les deux sites (ex. `mon-pack`).
4. **« Project Distribution » = « allow 3rd party distribution »** (sinon rien ne s'affiche).
5. Une image dont le **titre est exactement `MCPEDL`** (720×340px conseillé), parmi les
   **20 premières** du projet.
6. Activer l'**Author Rewards Program** dans les réglages du compte.

Une fois le **1er fichier approuvé** sur CF → le projet apparaît sur MCPEDL, et **toutes
les mises à jour suivantes se synchronisent automatiquement**.

### Manuel (1×) vs automatisable
| Étape | Qui |
|---|---|
| Créer le projet CF Bedrock + slug identique | **manuel** (l'API CF ne crée pas de projets) |
| Connexion comptes, distribution 3rd-party, Rewards, image « MCPEDL » | **manuel** (1×) |
| **Upload / mise à jour des fichiers** | ✅ **automatisable** (`publish.py --targets curseforge`) |
| Sync vers MCPEDL | ✅ **automatique** |

➡️ Workflow cible : `python3 publish.py --pack <slug> --targets curseforge` → le fichier
part sur CF → MCPEDL se met à jour **tout seul**.

## Ensuite : Marketplace officiel
Voir `10-bedrock-marketplace.md` (procédure officielle : minecraft.net/partner,
publiishers Pathway/Waypoint/Blocklab, prérequis, revenus 70/30).
