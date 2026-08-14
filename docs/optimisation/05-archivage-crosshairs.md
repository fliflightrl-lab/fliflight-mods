# Consolidation du cluster crosshair — bannières d'archivage

Décision : les 6 crosshairs secondaires redirigent vers le flagship **Dot Crosshair**
(le plus téléchargé : 24 415 dl). Les projets restent en ligne (les liens de
téléchargement restent actifs et ils gardent leur place dans les résultats de
recherche), mais leur description porte une bannière de consolidation.

## Bannière appliquée (en tête de description)
> **📌 Consolidated:** this crosshair is now part of the **Dot Crosshair** flagship — get the latest version there.

## Packs concernés
- CrossX Crosshair, Better Crosshair, Bigger Dot, CrosshairX, Sniper, Crossy.

## Effet attendu
- Les ~39 000 téléchargements du cluster se concentrent sur Dot Crosshair → rang ↑ → visibilité ↑.
- Le trafic de recherche « crosshair » atterrit sur un projet unique (meilleur social proof).

## Réversible
`python3 scripts/apply_archive.py` est idempotent (détecte la bannière déjà présente).
Pour revenir en arrière : supprimer la ligne `> **📌 Consolidated…**` du `body` dans
`packs/<slug>/manifest.json` puis re-publier la description sur Modrinth.
