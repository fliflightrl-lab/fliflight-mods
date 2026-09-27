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
