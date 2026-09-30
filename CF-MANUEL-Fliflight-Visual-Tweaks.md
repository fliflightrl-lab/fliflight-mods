# Guide manuel — Créer « Fliflight Visual Tweaks » sur CurseForge

Tout est prêt à copier-coller. Suis les étapes dans l'ordre.

---

## ÉTAPE 1 — Créer le projet parapluie

Va sur **https://legacy.curseforge.com/project/create** (connecté à ton compte).

| Champ | Valeur à coller |
|---|---|
| **Game** | Minecraft |
| **Category** | Resource Packs |
| **Name** | `Fliflight Visual Tweaks` |
| **Summary** | `Small visual tweaks for Minecraft Java: clear lava, clear spyglass, clear powder snow, thin totem and a clean hotbar. Pick the file you want.` |
| **Primary Category** | 16x |
| **License** | All Rights Reserved |
| **Allow untrusted distribution** | ✅ Oui |
| **Logo** | `dist/cf_logos/fliflight-visual-tweaks-512.png` (512×512) |

### Description (colle-la en mode SOURCE / HTML de l'éditeur)

```html
<p><strong>Fliflight Visual Tweaks</strong> is a set of small, client-side resource packs that each change one specific thing about the vanilla look — and nothing else. Pick the tweak you want from the <strong>Files</strong> tab.</p>

<h3>Available tweaks (one file each)</h3>
<ul>
<li><strong>Clear Lava</strong> — lava becomes semi-transparent so you can see the terrain before jumping in</li>
<li><strong>Clear Spyglass</strong> — removes the dark scope overlay, giving you a full-screen zoom</li>
<li><strong>Clear Powder Snow</strong> — removes the frosty screen overlay when you sink into powder snow</li>
<li><strong>Thin Totem</strong> — a slimmer totem that no longer covers the middle of your screen</li>
<li><strong>Clean Hotbar</strong> — a flat, minimal hotbar without the dark background</li>
</ul>

<h3>What they all have in common</h3>
<ul>
<li>Change <strong>only</strong> what is listed above — nothing else</li>
<li><strong>Client-side only</strong>: they work on any server and no one else needs them</li>
<li>16x, matching the vanilla resolution exactly</li>
</ul>

<h3>Install</h3>
<ol>
<li>Open the <strong>Files</strong> tab and download the .zip for the tweak you want (do not unzip it).</li>
<li>Drop it into .minecraft/resourcepacks — or use the CurseForge app.</li>
<li>Enable it in <strong>Options → Resource Packs</strong> and move it to the top of the list.</li>
</ol>

<p>Works on Minecraft <strong>1.21.x</strong> (Java Edition) and most launchers.</p>

<hr>
<p>This is part of the <strong>PvP Essentials</strong> family — the all-in-one pack with crosshair, visible ores, short sword, low fire and clear pumpkin: <a href="https://www.curseforge.com/minecraft/texture-packs/pvp-essentials-crosshair-visible-ores-sword-low">PvP Essentials</a></p>
<p>Liked it? Support the work on <a href="https://ko-fi.com/fliflight">Ko-fi</a>.</p>
```

---

## ÉTAPE 2 — Uploader les 5 variantes en fichiers séparés

Sur la page du projet → **Files → Upload file**. Pour CHAQUE fichier ci-dessous, mets le **Display name** indiqué, coche les **versions**, et colle le **changelog**. Les zips sont dans `dist/TESTEZ-MOI/`.

### Fichier 1 — Clear Lava
- **Fichier** : `fliflight-clear-lava-1.0.0-resourcepack-1.21.4.zip`
- **Display name** : `Clear Lava`
- **Changelog** : `Initial release: semi-transparent lava.`
- **Versions** (17) : 1.19, 1.19.2, 1.19.4, 1.20, 1.20.1, 1.20.2, 1.20.4, 1.20.5, 1.20.6, 1.21, 1.21.1, 1.21.3, 1.21.4, 1.21.5, 1.21.6, 1.21.7, 1.21.8

### Fichier 2 — Clear Spyglass
- **Fichier** : `fliflight-clear-spyglass-1.0.0-resourcepack-1.21.4.zip`
- **Display name** : `Clear Spyglass`
- **Changelog** : `Initial release: spyglass scope overlay removed.`
- **Versions** (17) : identiques à Clear Lava

### Fichier 3 — Clear Powder Snow
- **Fichier** : `fliflight-clear-powder-snow-1.0.0-resourcepack-1.21.4.zip`
- **Display name** : `Clear Powder Snow`
- **Changelog** : `Initial release: frost overlay removed.`
- **Versions** (17) : identiques à Clear Lava

### Fichier 4 — Thin Totem
- **Fichier** : `fliflight-thin-totem-1.0.0-resourcepack-1.21.4.zip`
- **Display name** : `Thin Totem`
- **Changelog** : `Initial release: thinner totem texture.`
- **Versions** (17) : identiques à Clear Lava

### Fichier 5 — Clean Hotbar
- **Fichier** : `fliflight-clean-hotbar-1.0.0-resourcepack-1.21.4.zip`
- **Display name** : `Clean Hotbar`
- **Changelog** : `Initial release: flat clean hotbar + XP bar.`
- **Versions** (6) : 1.21.3, 1.21.4, 1.21.5, 1.21.6, 1.21.7, 1.21.8 ⚠️ *(le hotbar ne marche que sur 1.21.3+, c'est normal)*

> 💡 Ordre conseillé : upload Clear Lava **en dernier** (il deviendra le fichier « Latest » affiché par défaut).

---

## ÉTAPE 3 — Les 3 packs encore en attente (surveille-les)

Ces 3 projets CF ne sont **pas encore refusés** mais ont le même profil que les 5 refusés. S'ils reçoivent aussi « Merge Projects », ajoute-les comme 6e/7e/8e fichiers du parapluie (mêmes infos) :

| Pack | CF id | Fichier zip | Display name |
|---|---|---|---|
| Clear Water | 1716911 | `fliflight-clear-water-1.0.0-resourcepack-1.21.4.zip` | `Clear Water` |
| Low Shield | 1716894 | `fliflight-low-shield-1.0.0-resourcepack-1.21.4.zip` | `Low Shield` |
| No Dark Corners | 1716909 | `fliflight-no-dark-corners-1.0.0-resourcepack-1.21.4.zip` | `No Dark Corners` |

Leurs résumés (si besoin) :
- **Clear Water** : `Makes water translucent so you can see the seabed, ores and mobs while swimming.`
- **Low Shield** : `Shrinks and lowers the first-person shield so it stops covering your screen in fights.`
- **No Dark Corners** : `Removes the dark shading in the corners of the screen, so the whole view stays evenly lit.`

---

## ÉTAPE 4 — Les 3 packs déjà en ligne (ne touche à rien)

| Pack | CF id | Statut |
|---|---|---|
| Low Fire | 1653138 | en ligne |
| Clear Pumpkin | 1653159 | en ligne |
| PvP Essentials | 1653188 | en ligne |

---

## Emplacement des fichiers

- **Zips** : `~/fliflight-mods/dist/TESTEZ-MOI/` (les 9 zips, dont les 5 à uploader)
- **Logo du parapluie** : `~/fliflight-mods/dist/cf_logos/fliflight-visual-tweaks-512.png`
- **Icônes individuelles** : `~/fliflight-mods/dist/cf_logos/<pack>-512.png`
