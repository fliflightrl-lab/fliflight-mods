# 🧪 Test des 8 nouveaux packs — Fliflight

**Comment tester :** copie les 8 zips depuis `~/fliflight-mods/dist/` dans ton dossier `%appdata%\.minecraft\resourcepacks\`, puis **active UN pack à la fois** (sinon tu ne verras pas quelle modification fait quoi).

> 💡 Les 8 zips sont aussi dans `packs/<slug>/files/`.

---

## 1. Low Shield - See Past Your Shield

*Shrinks and lowers the first-person shield so it stops covering your screen in fights.*

- **Zip à tester :** `fliflight-low-shield-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-low-shield\files\fliflight-low-shield-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/low-shield-shield-out-of-the-way
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-low-shield

**À vérifier en jeu :**
- [ ] Prends un bouclier dans la main ou l'offhand, passe en vue 1re personne.
- [ ] Le bouclier doit être NETTEMENT plus petit et plus bas (45 % plus petit).
- [ ] Bloque (clic droit) : le centre de l'écran doit rester dégagé.
- [ ] ⛔ Si le bouclier est toujours aussi gros ou a disparu → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 2. No Dark Corners

*Removes the dark shading in the corners of the screen, so the whole view stays evenly lit.*

- **Zip à tester :** `fliflight-no-dark-corners-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-no-vignette\files\fliflight-no-dark-corners-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/no-vignette-clear-screen-corners
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-no-vignette

**À vérifier en jeu :**
- [ ] Regarde les 4 coins de l'écran, de jour ET de nuit.
- [ ] Aucun assombrissement dans les coins (l'écran est uniforme).
- [ ] ⛔ Si les coins restent sombres → cassé. Si l'écran est tout noir → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 3. Clear Water - See Through Water

*Makes water translucent so you can see the seabed, ores and mobs while swimming.*

- **Zip à tester :** `fliflight-clear-water-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-clear-water\files\fliflight-clear-water-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/clear-water-see-through-water
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-clear-water

**À vérifier en jeu :**
- [ ] Plonge dans l'eau et regarde vers le bas.
- [ ] Tu dois VOIR le fond (sable/gravats) et les mobs à travers l'eau.
- [ ] Sous l'eau, le voile bleu plein écran doit avoir disparu.
- [ ] ⛔ Si l'eau est toujours opaque → cassé. Si l'eau a totalement disparu → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 4. Clear Lava - See Through Lava

*Makes lava semi-transparent so you can see the terrain underneath before you jump in.*

- **Zip à tester :** `fliflight-clear-lava-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-clear-lava\files\fliflight-clear-lava-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/clear-lava-see-through-lava
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-clear-lava

**À vérifier en jeu :**
- [ ] Place-toi au-dessus d'une flaque de lave et regarde dedans.
- [ ] La lave doit être semi-transparente (on voit le netherrack dessous).
- [ ] ⛔ Si la lave est toujours opaque → cassé. Si la lave est invisible → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 5. Clear Spyglass - Full Screen Zoom

*Removes the spyglass scope overlay so the full screen stays usable while you zoom.*

- **Zip à tester :** `fliflight-clear-spyglass-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-clear-spyglass\files\fliflight-clear-spyglass-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/clear-spyglass-no-scope-overlay
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-clear-spyglass

**À vérifier en jeu :**
- [ ] Prends une longue-vue et utilise-la (clic droit).
- [ ] Aucun masque noir de viseur : la vue est dégagée sur tout l'écran.
- [ ] ⛔ Si le cercle noir est toujours là → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 6. Clean Hotbar - Flat Minimal HUD

*Replaces the vanilla hotbar and XP bar with a flat design that is easier to read at a glance.*

- **Zip à tester :** `fliflight-clean-hotbar-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-clean-hotbar\files\fliflight-clean-hotbar-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/clean-hotbar-flat-minimal-hud
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-clean-hotbar

**À vérifier en jeu :**
- [ ] Regarde ta barre d'objets en bas (nécessite 1.21.3+).
- [ ] Fond plat et sobre, 9 cases visibles, cadre fin et clair.
- [ ] La barre d'XP doit être vert vif et nette.
- [ ] ⛔ Si la barre reste l'ancienne → cassé (vérifie ta version de MC).

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 7. Thin Totem - Smaller Totem Pop

*Slims the totem of undying so its pop animation stops blocking your view mid-fight.*

- **Zip à tester :** `fliflight-thin-totem-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-thin-totem\files\fliflight-thin-totem-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/thin-totem-slimmer-totem-pop
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-thin-totem

**À vérifier en jeu :**
- [ ] Pop un totem (ou regarde-le dans l'inventaire).
- [ ] Le totem doit être nettement plus fin (7 px de large au lieu de 16).
- [ ] ⛔ Si le totem est coupé au milieu ou invisible → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 8. Clear Powder Snow - No Freeze Overlay

*Removes the frost overlay so you can still see where you are going while freezing.*

- **Zip à tester :** `fliflight-clear-powder-snow-1.0.0-resourcepack-1.21.4.zip`
- **Dossier local :** `C:\Users\user\fliflight-mods\packs\fliflight-clear-powder-snow\files\fliflight-clear-powder-snow-1.0.0-resourcepack-1.21.4.zip`
- **CurseForge :** https://www.curseforge.com/minecraft/texture-packs/clear-powder-snow-no-frost-overlay
- **Modrinth :** https://modrinth.com/resourcepack/fliflight-clear-powder-snow

**À vérifier en jeu :**
- [ ] Entre dans de la poudreuse et reste dedans jusqu'à geler.
- [ ] Aucun voile de givre sur les bords de l'écran.
- [ ] ⛔ Si le givre est toujours là → cassé.

**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________

---

## 📋 Récap à me renvoyer

| # | Pack | OK ? | Problème constaté |
|---|---|---|---|
| 1 | Low Shield - See Past Your Shield | ☐ | |
| 2 | No Dark Corners | ☐ | |
| 3 | Clear Water - See Through Water | ☐ | |
| 4 | Clear Lava - See Through Lava | ☐ | |
| 5 | Clear Spyglass - Full Screen Zoom | ☐ | |
| 6 | Clean Hotbar - Flat Minimal HUD | ☐ | |
| 7 | Thin Totem - Smaller Totem Pop | ☐ | |
| 8 | Clear Powder Snow - No Freeze Overlay | ☐ | |
