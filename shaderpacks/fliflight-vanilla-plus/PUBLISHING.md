# Publication — Vanilla+ Potato Shader

## Plateformes

| Plateforme | Référence | État |
|---|---|---|
| **CurseForge** | projet **1721227** — <https://legacy.curseforge.com/minecraft/shaders/vanilla-potato-shader> | en revue (`Processing`) |
| **Modrinth** | `vanilla-potato-shader` (id `pSuQ25bN`) — <https://modrinth.com/shader/vanilla-potato-shader> | `processing` |
| **GitHub** | release `fliflight-vanilla-plus-v0.8.1` (asset 18 990 o) | publiée, marquée Latest |

## CurseForge — identifiants à réutiliser

- **Projet** : `1721227` (jeu 432 = Minecraft, catégorie 6552 = Shaders)
- **Fichier v0.9** : id `9029781` — `Vanilla+ Potato Shader v0.9 - Potato`, 21,16 Ko,
  versions 1.21 → 1.21.8 (9 entrées), statut `Processing`
- **Catégorie primaire** : *Realistic* (6553). **Vanilla (6555) est `disabled` sur ce compte**
  et Fantasy (6554) ne correspond pas au contenu.
- **Licence** : All Rights Reserved · **Langue** : enUS · distribution autorisée
- **Galerie** : 9 captures légendées, ids `1997729`–`1997738`
  (⚠️ `1997739` est un doublon de « WARM TORCH LIGHT » issu d'un test de vérification :
  à supprimer à la main depuis la page `.../screenshots`, la suppression en ligne de commande
  est impossible — le lien `delete-prompt` n'a pas de jeton CSRF exploitable)

## Upload du fichier (API)

```bash
# metadata.gameVersions doit contenir des ENTIERS (voir dist/cf_version_ids.json ; 1.21.4 = 12281)
curl -X POST "https://minecraft.curseforge.com/api/projects/1721227/upload-file" \
  -H "X-Api-Token: <token UUID>" \
  -F 'metadata={"changelog":"...","changelogType":"text","displayName":"...","releaseType":"release","gameVersions":[11457,11779,12079,12084,12281,12934,13422,13506,13620]}' \
  -F "file=@dist/shaderpacks/FliflightVanillaPlus-v0.9-Potato.zip"
```

## Galerie en masse

`scripts/cf_gallery_upload.py 1721227 dist/shader_gallery dist/shader_captions.json`

Une image à la fois côté CurseForge, et **les noms de champs changent à chaque affichage** :
le script relit le formulaire avant chaque envoi. Le fichier de cookies attendu
(`dist/cf_cookies.json`) contient une session active — à supprimer après usage.

## Réglages de la fiche

- Résumé : une ligne orientée bénéfice (« A lightweight vanilla-plus shader: no fog, … »)
- Description : fonction → pourquoi → installation → versions, liens promo **en bas**
- Bloc de soutien : « Everything here is free, and it stays free. » + Ko-fi + linktr.ee
- Logo : `dist/shader_icon/vanilla-potato-shader-512.png` (512×512)
