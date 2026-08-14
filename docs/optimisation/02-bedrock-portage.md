# B — Portage Bedrock + candidature Marketplace

## Constat (issu de l'inspection des packs)
| Pack | Contenu Java | Portage Bedrock |
|---|---|---|
| Crosshairs (×7) | 1 PNG `gui/sprites/hud/crosshair.png` | ❌ **non portable** — le crosshair Bedrock n'est pas remplaçable par resource pack |
| Visible Ores | ~20 PNG `textures/block/*_ore.png` + blockstates/models | ✅ simple (mapping `block/` → `blocks/`) |
| Pvp sword | 6 PNG `textures/item/*_sword.png` | ✅ simple (mapping `item/` → `items/`) |

➡️ **L'opportunité Bedrock = `visible-ores` + `pvp-sword`** (plus de nouveaux packs
pensés Bedrock-natifs). Le cluster crosshair n'a pas de débouché Bedrock.

## Conversion automatique (script fourni)
```bash
python3 scripts/build_mcpack.py \
  --zip packs/visible-ores-all-versions-and-netherite/files/visible_ores-1.0.0-resourcepack-.zip \
  --out dist/bedrock/visible-ores.mcpack \
  --name "Visible Ores" \
  --description "See every ore and netherite clearly" \
  --icon packs/visible-ores-all-versions-and-netherite/icon.png

python3 scripts/build_mcpack.py \
  --zip packs/pvp-sword-little-sword-all-versions/files/better_little_sword-1.0.0-resourcepack-1.21.4.zip \
  --out dist/bedrock/pvp-sword.mcpack \
  --name "Short Sword" \
  --description "Smaller swords for PvP" \
  --icon packs/pvp-sword-little-sword-all-versions/icon.png
```
Le `.mcpack` (zip renommé) contient `manifest.json` (UUIDs générés) + `pack_icon.png`
+ `textures/blocks/*.png` ou `textures/items/*.png`.

## Limites à connaître
- Le `.mcpack` **déposé sur MCPEDL/CurseForge Bedrock** marche immédiatement
  (les joueurs l'installent en un clic). Teste d'abord sur ton propre compte.
- Les `blockstates/*.json` et `models/` Java **n'existent pas** en Bedrock : le script
  les ignore (l'effet « minerai visible » vient des PNG seuls — ok pour la plupart des cas).
- Le **Marketplace officiel** exige un niveau de qualité supérieur (UI/UX, icône 512×512,
  description, versions testées) — différent d'un simple dépôt communautaire.

## Candidature Marketplace (Microsoft)
1. Crée/connecte un compte **Microsoft Partner** : https://partner.microsoft.com → programme
   « Minecraft Marketplace » (partner platform Minecraft).
2. Remplis le dossier : portfolio (tes packs), identité (individuel OK, pas besoin d'entreprise),
   et **du contenu original**. Le portage de TES packs est accepté ; la revente de packs tiers non.
3. Si accepté : tu publies via le portail partenaire, prix en **Minecoins**, rémunération versée
   par Microsoft (commission plateforme ~30 %). C'est la seule piste qui change l'ordre de
   grandeur de tes revenus.
4. En attendant l'acceptation : dépose `visible-ores.mcpack` + `pvp-sword.mcpack` sur
   **MCPEDL** (audience Bedrock énorme, gratuit, trafic immédiat) pour commencer à capter
   l'audience Bedrock sans attendre le Marketplace.
