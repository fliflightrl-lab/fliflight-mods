# Publication — Everlight

## Plateformes

| Plateforme | Référence | État |
|---|---|---|
| **CurseForge** | projet **1722417** — [everlight-see-in-the-dark](https://legacy.curseforge.com/minecraft/texture-packs/everlight-see-in-the-dark) | `Under Review` (le fichier est en revue) |
| **Modrinth** | id **SpSDt80D** — [fliflight-everlight](https://modrinth.com/resourcepack/fliflight-everlight) | `processing` |
| **GitHub** | release **everlight-v1.0.0** | publiée, *Latest* |

## CurseForge — identifiants réutilisables

- **Projet** : `1722417` (jeu 432 = Minecraft, catégorie 12 = Resource Packs)
- **Fichier** : `fliflight-everlight-1.0.0-resourcepack-1.21.4.zip` — 31,65 Ko, **1.21.8 +16** (= les 17 versions), `Under Review`
- **Catégorie primaire** : `16x` (**id 393**) · tag de jeu : *Miscellaneous* (**405**)
  ⚠️ `ModJam 2025` (8939) est `disabled` sur ce compte — comme `Vanilla` l'était pour les shaders
- **Licence** : All Rights Reserved · **Langue** : enUS · distribution autorisée
- **Galerie** : 4 images, ids `2000287`–`2000290`
  1. `A cave, before and after` ← *featured*
  2. `The same spot at night, before and after`
  3. `The Nether`
  4. `The End`

## Recette de création (le formulaire se soumet, mais ne redirige JAMAIS)

1. `/project/create` → jeu « Minecraft », catégorie « Resource Packs » (12).
   Le vrai formulaire s'affiche **sur la même URL** — attendre `#field-name`, pas une redirection.
2. Remplir : nom, résumé (setter natif), description (TinyMCE), licence 1, catégorie **393**,
   langue 2, distribution `t`, tag **405**, `#field-screenshot` (icône 512×512).
3. **Cocher les versions de jeu** — `#field-game-version-<jeu>-<version>`, la valeur étant
   l'id entier (`dist/cf_version_ids.json`). Sans ça le POST est refusé avec
   « You must select at least one version from the minecraft group of versions ».
4. `#field-file` (le zip) est **requis** : le glisser via CDP suffit, il est uploadé par la page.
5. Vérifier `jQuery.data(form,'validator').form()` → `true`, puis `form.requestSubmit()`.
   **Aucune redirection n'arrive** : le projet est créé malgré tout. Vérifier à l'URL publique.
6. ⚠️ Ne JAMAIS soumettre le premier `<form>` de la page : c'est **Sign Out**, ça déconnecte le compte.

## Galerie en masse

```bash
python scripts/cf_gallery_upload.py 1722417 packs/fliflight-everlight/gallery dist/everlight_captions.json
```

Le script relit le formulaire avant chaque image (les noms de champs sont des hash régénérés à
chaque affichage) et pose **titre + description**. Il attend une session dans
`dist/cf_cookies.json` — à supprimer après usage.

## Modrinth — un défaut à corriger à la main

Les 4 captures sont en ligne **sans titre** : `PATCH /project/{id}/gallery?url=...` répond `204`
sans rien appliquer (testé avec le paramètre encodé et avec l'URL dans le corps). À poser dans
**Settings → Gallery** de la page du projet.

## Reconstruction

```bash
python scripts/build_fullbright.py            # pack, icône, manifeste (galerie lue depuis le disque)
python scripts/publish_pack_modrinth.py fliflight-everlight   # idempotent
```
