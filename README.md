# Fliflight — pipeline de publication multi-plateforme

Une seule commande (ou un clic dans GitHub Actions) publie un pack vers
**Modrinth**, **CurseForge**, **GitHub Releases** et prépare le dépôt manuel
**Planet Minecraft**.

> ☕ **Soutenir le projet → [ko-fi.com/fliflight](https://ko-fi.com/fliflight)**
> Tous les packs restent **gratuits** — Ko-fi finance les mises à jour et les nouveaux packs.

```
packs/<slug>/
    manifest.json        # source de vérité (métadonnées + ids + version)
    files/<fichier>      # zip / jar
    icon.<ext>
    gallery/<i>.<ext>
publish.py               # l'outil unique (local == CI)
scripts/gen_manifests.py # migration depuis l'ancien miroir (~/curseforge-to-modrinth)
.github/workflows/publish.yml
```

## Usage local

```bash
# Vérif (lecture seule, sans effet) — à lancer après tout changement
python3 publish.py --verify

# Publier un pack partout (sauf CF, voir note) — mode essai d'abord
python3 publish.py --pack crossx --targets modrinth,github,pmc --dry-run

# Vraie publication
python3 publish.py --pack crossx --targets modrinth,github,pmc

# Tous les packs
python3 publish.py --all --targets pmc
```

## Identifiants

Lus depuis les variables d'env, sinon `~/.config/fliflightmc/credentials.json` :

| Variable    | Cible       | Source |
|-------------|-------------|--------|
| `MR_TOKEN`  | Modrinth    | modrinth.com/settings/pats (scopes: créer/updater projet + versions) |
| `CF_API_KEY`| CurseForge  | console.curseforge.com → Add API Key |
| `GH_TOKEN`  | GitHub Releases | GitHub → Settings → Developer settings → PAT (scope `repo`) |
| `GH_REPO`   | GitHub Releases | `owner/repo` (auto en CI via `github.repository`) |

## Publier une mise à jour

1. Remplace le fichier dans `packs/<slug>/files/`.
2. Bump `version.number` dans `packs/<slug>/manifest.json` (+ `version.changelog`).
3. `python3 publish.py --verify` puis `python3 publish.py --pack <slug> --dry-run`.
4. Lance la vraie publication (local ou via GitHub Actions → *Run workflow*).

## CurseForge (upload) — RÉSOLU

CurseForge expose **deux APIs avec deux tokens différents** — c'est le piège :

| API | Base URL | Header | Type de token |
|---|---|---|---|
| Lecture (Eternal) | `api.curseforge.com` | `x-api-key` | clé bcrypt `$2a$10$…` |
| **Upload** | `minecraft.curseforge.com/api` | `X-Api-Token` | **token auteur UUID** |

Le token d'upload se génère sur **https://www.curseforge.com/account/api-tokens**
(format UUID, ex. `0556e0a9-…`) — **pas** sur console.curseforge.com. Un token
bcrypt est rejeté par l'API d'upload avec `API token is malformed`.

Credentials (`~/.config/fliflightmc/credentials.json`) :

```json
{ "curseforge": { "api_key": "…", "author_id": 123880127, "upload_token": "…" } }
```

`publish.py` utilise `api_key` pour résoudre les game-versions et `upload_token`
pour le `POST /projects/{id}/upload-file`.

## Planet Minecraft

PMC n'a **pas d'API d'upload publique** (domaine derrière Cloudflare). La cible
`pmc` génère un **kit prêt à déposer** dans `dist/pmc/<slug>/` (fichier + icône +
galerie + `UPLOAD.md` avec titre/description/tags pré-remplis). Dépôt manuel ~2 min
sur planetminecraft.com.

## Registre des projets

**[`PROJECTS.md`](PROJECTS.md)** — liste tous les projets avec leurs ids CurseForge /
Modrinth et leur version. Fichier **généré** :

```bash
python3 scripts/gen_project_registry.py
```

Il lit `packs/*/manifest.json` (donc toujours synchronisé) et y ajoute l'état des
projets hors pipeline (shader pack, mods Fabric). Ne pas l'éditer à la main.

## Shader pack — `shaderpacks/fliflight-vanilla-plus/`

Pack de shader client **Vanilla+** profil **Potato** pour Minecraft Java 1.21.x
(OptiFine / Iris). **Hors pipeline `packs/`** : pas encore publié sur CurseForge /
Modrinth, les binaires sont attachés aux GitHub Releases.

**Version de référence : `v0.8.1` — la seule entièrement fonctionnelle.**
Les versions antérieures sont conservées uniquement comme historique dans `PROJECTS.md` ;
ne pas les livrer.

Effets : aucun brouillard, bloom (2 passes, buffer demi-résolution), feuillage qui ondule,
eau animée, lumière teintée (torches chaudes / ciel froid), lumière directionnelle, ciel
avec halo solaire et lunaire + étoiles + bande d'aube, brume d'horizon, étalonnage par heure.

**Les ombres ne sont pas livrées** (trois tentatives, trois artefacts ; cause racine de la
v0.8 corrigée et prouvée, mais le symptôme suivant non expliqué). Le programme d'ombre n'est
même pas embarqué dans le zip, donc OptiFine ne fait aucune passe d'ombre. Détail complet et
pistes restantes dans `shaderpacks/fliflight-vanilla-plus/README.md`.

### Outillage du shader pack

```bash
python3 scripts/validate_shader.py shaderpacks/fliflight-vanilla-plus  # erreurs a ecran noir silencieux
python3 scripts/rebuild_shaderzip.py --test                            # build de test
bash scripts/of_compile_test.sh <etiquette>                            # compilation reelle (OptiFine hors ligne)
python3 scripts/rebuild_shaderzip.py                                   # livraison
```

`validate_shader.py` attrape les erreurs qui donnent un écran noir sans message :
`#include` sans extension, `DRAWBUFFERS` manquant, littéraux flottants malformés,
varyings absents du vertex, uniformes déclarés en double, variable locale redéclarée,
sampler d'ombre mal nommé.

`of_compile_test.sh` lance OptiFine en `launchwrapper` avec `--quickPlaySingleplayer`
(ce qui force la compilation des `gbuffers_*`) et lit `logs/latest.log`.

> **Piège du test de compilation** : OptiFine charge le pack **déjà sélectionné**, pas le
> dernier fichier déposé. Un build écrit sous un nouveau nom valide donc l'ancien code.
> Le mode `--test` écrase tous les `FliflightVanillaPlus-*.zip` présents pour rendre cela
> impossible, et il faut **vérifier le NOMBRE de programmes chargés** attendu, pas seulement
> l'absence d'erreur.

