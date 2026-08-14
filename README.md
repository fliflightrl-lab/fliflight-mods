# Fliflight — pipeline de publication multi-plateforme

Une seule commande (ou un clic dans GitHub Actions) publie un pack vers
**Modrinth**, **CurseForge**, **GitHub Releases** et prépare le dépôt manuel
**Planet Minecraft**.

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

## ⚠️ CurseForge (upload)

- L'upload automatique **vers** CurseForge passe par `minecraft.curseforge.com/api`
  (endpoint `/projects/{id}/upload-file`, header `X-Api-Token`).
- La clé actuelle (`$2a$10$…`) est **acceptée par l'API de lecture**
  (`api.curseforge.com`, `x-api-key`) mais **rejetée comme « malformed » par l'API
  d'upload**. Il faut probablement générer une nouvelle clé depuis
  console.curseforge.com pour débloquer l'upload API.
- En attendant, CurseForge reste une **source** (tu publies sur le site CF comme
  d'habitude) et le pipeline pousse CF → Modrinth/GitHub/PMC. C'est le sens
  inverse (`--targets` sans `curseforge`) qui est automatisé et fiable.

## Planet Minecraft

PMC n'a **pas d'API d'upload publique** (domaine derrière Cloudflare). La cible
`pmc` génère un **kit prêt à déposer** dans `dist/pmc/<slug>/` (fichier + icône +
galerie + `UPLOAD.md` avec titre/description/tags pré-remplis). Dépôt manuel ~2 min
sur planetminecraft.com.
