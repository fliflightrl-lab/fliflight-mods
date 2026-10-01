# Registre des projets - FliflightMC

Genere le 2026-10-01 par `scripts/gen_project_registry.py` - **ne pas editer a la main**.

21 projets dans le pipeline `packs/`. Les binaires ne sont pas dans le depot : ils sont attaches aux **GitHub Releases** (voir `publish.py`).

## Projets publies (pipeline `packs/`)

| Projet | Type | CurseForge | Modrinth | Version |
|---|---|---|---|---|
| Diamond Dimension — A New World Made of Diamonds (NeoForge) | mod | [1479652](https://www.curseforge.com/projects/1479652) | [NR54mkOD](https://modrinth.com/project/NR54mkOD) | 1.0.0 |
| Bigger Dot Crosshair — High-Visibility PvP Crosshair | resourcepack | [1499072](https://www.curseforge.com/projects/1499072) | [d8t14H03](https://modrinth.com/project/d8t14H03) | 1.0.0 |
| CrosshairX — Enhanced Crosshair for PvP | resourcepack | [1497428](https://www.curseforge.com/projects/1497428) | [Y8zhQ9z5](https://modrinth.com/project/Y8zhQ9z5) | 1.0.0 |
| Sniper Crosshair — Precision for Bow & Long-Range PvP | resourcepack | [1588694](https://www.curseforge.com/projects/1588694) | [4JKFVXUw](https://modrinth.com/project/4JKFVXUw) | 1.0.0 |
| Better Crosshair — Modern Clean Crosshair for PvP | resourcepack | [1494020](https://www.curseforge.com/projects/1494020) | [oBGsX8oY](https://modrinth.com/project/oBGsX8oY) | 1.0.0 |
| CrossX Crosshair — Custom PvP Crosshair Pack | resourcepack | [1499029](https://www.curseforge.com/projects/1499029) | [1ylCihJa](https://modrinth.com/project/1ylCihJa) | 1.0.0 |
| Crossy Crosshair — Stylish PvP Crosshair | resourcepack | [1558798](https://www.curseforge.com/projects/1558798) | [sQkn3uEf](https://modrinth.com/project/sQkn3uEf) | 1.0.0 |
| Dot Crosshair — Clean PvP & Survival Crosshair (All Versions) | resourcepack | [1499007](https://www.curseforge.com/projects/1499007) | [4r8Ufv9p](https://modrinth.com/project/4r8Ufv9p) | 1.0.0 |
| Clean Hotbar - Flat Minimal HUD | resourcepack | [1716921](https://www.curseforge.com/projects/1716921) | [PDnvunp5](https://modrinth.com/project/PDnvunp5) | 1.0.0 |
| Clear Lava - See Through Lava | resourcepack | [1716914](https://www.curseforge.com/projects/1716914) | [eG9N5405](https://modrinth.com/project/eG9N5405) | 1.0.0 |
| Clear Powder Snow - No Freeze Overlay | resourcepack | [1716925](https://www.curseforge.com/projects/1716925) | [fQlGVRS8](https://modrinth.com/project/fQlGVRS8) | 1.0.1 |
| Clear Pumpkin - No Pumpkin Blur | resourcepack | [1653159](https://www.curseforge.com/projects/1653159) | [xnQODGjN](https://modrinth.com/project/xnQODGjN) | 1.0.0 |
| Clear Spyglass - Full Screen Zoom | resourcepack | [1716918](https://www.curseforge.com/projects/1716918) | [HEAEl6k5](https://modrinth.com/project/HEAEl6k5) | 1.0.0 |
| Clear Water - See Underwater | resourcepack | [1716911](https://www.curseforge.com/projects/1716911) | [4KyMcPC1](https://modrinth.com/project/4KyMcPC1) | 1.0.0 |
| Low Fire — Lowered Flame Overlay (Full Animation) | resourcepack | [1653138](https://www.curseforge.com/projects/1653138) | [RIH3vxZQ](https://modrinth.com/project/RIH3vxZQ) | 1.0.0 |
| Low Shield - See Past Your Shield | resourcepack | [1716894](https://www.curseforge.com/projects/1716894) | [3kHplXd9](https://modrinth.com/project/3kHplXd9) | 1.0.0 |
| No Dark Corners | resourcepack | [1716909](https://www.curseforge.com/projects/1716909) | [JYyEzln5](https://modrinth.com/project/JYyEzln5) | 1.0.0 |
| PvP Essentials | resourcepack | [1653188](https://www.curseforge.com/projects/1653188) | [cHpwGcrb](https://modrinth.com/project/cHpwGcrb) | 1.0.5 |
| Short Sword | resourcepack | [1334714](https://www.curseforge.com/projects/1334714) | [IcIJjhMO](https://modrinth.com/project/IcIJjhMO) | 1.0.0 |
| Thin Totem - Smaller Totem Pop | resourcepack | [1716922](https://www.curseforge.com/projects/1716922) | [32hlofGi](https://modrinth.com/project/32hlofGi) | 1.0.0 |
| Visible Ores — See Every Ore & Netherite (Shaders Ready) | resourcepack | [1334611](https://www.curseforge.com/projects/1334611) | [SEfn6MDy](https://modrinth.com/project/SEfn6MDy) | 1.0.0 |

## Shader pack (`shaderpacks/fliflight-vanilla-plus/`)

Hors pipeline : pas encore publie sur CurseForge / Modrinth (decision : plus tard).
Cible Minecraft Java 1.21.x, OptiFine / Iris. Profil **Potato**.

| Version | Contenu | Etat |
|---|---|---|
| v0.1 | no-fog + etalonnage | livree, validee en jeu |
| v0.2 | + bloom, ombres, feuillage, ciel | bloom non compile (litteral 1.5.0) |
| v0.3 | Potato : ombres allegees | voile noir |
| v0.3.1 | fix ecran bleu | brume d'horizon basee sur `far` -> ecran bleu |
| v0.4 | normale en espace monde | composite non compile -> ecran blanc |
| v0.5 | fix ecran blanc, ombres desactivees | fonctionnelle |
| v0.6 | alphaTest + une passe plein ecran en moins | fonctionnelle |
| v0.7 | lumiere teintee, eau animee, ciel etoile | fonctionnelle |
| v0.8 | ombres reactivees, bloom demi-res, brume | ombres buggees |
| **v0.8.1** | ombres retirees, bloom demi-res, brume | **SEULE VERSION ENTIEREMENT FONCTIONNELLE** |

### Effets actifs dans la version livree (v0.8.1)

Aucun brouillard, bloom (2 passes, buffer demi-resolution), feuillage qui ondule, eau animee, lumiere teintee (torches chaudes / ciel froid), lumiere directionnelle, ciel avec halo solaire et lunaire + etoiles + bande d'aube, brume d'horizon, etalonnage par heure.

### Non livre : les ombres

Trois tentatives, trois artefacts differents. La cause racine de la v0.8 etait reelle et prouvee (dans une passe d'ombre `gl_ModelViewMatrix` est la matrice d'ombre, donc `gbufferModelViewInverse` dessus donne une position monde absurde), mais le symptome suivant - ombres buggees dans un perimetre autour du joueur et clignotantes - n'est pas explique. Retirees du zip : OptiFine ne fait donc aucune passe d'ombre.

Pistes non testees, documentees dans le README du pack : distorsion non uniforme de `shadowProjection` centree sur le joueur (BSL la compense des deux cotes), et l'uniform `shadowFade` ignore.

## Mods Fabric (`mods/`)

- `custom-crosshair`
- `pvphud`

