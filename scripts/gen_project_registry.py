"""Genere PROJECTS.md : registre de tous les projets FliflightMC.

Source de verite : les manifests de packs/*/manifest.json (donc toujours a jour),
plus les sections qui ne passent pas par le pipeline (shader pack, mods Fabric).

Usage: python scripts/gen_project_registry.py
"""

import json
import os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "PROJECTS.md")

# Etat des versions du shader pack. Sert de memoire du projet : ce qui a ete livre,
# ce qui a casse, et ce qui est reellement utilisable.
SHADER_HISTORY = [
    ("v0.1", "no-fog + etalonnage", "livree, validee en jeu"),
    ("v0.2", "+ bloom, ombres, feuillage, ciel", "bloom non compile (litteral 1.5.0)"),
    ("v0.3", "Potato : ombres allegees", "voile noir"),
    ("v0.3.1", "fix ecran bleu", "brume d'horizon basee sur `far` -> ecran bleu"),
    ("v0.4", "normale en espace monde", "composite non compile -> ecran blanc"),
    ("v0.5", "fix ecran blanc, ombres desactivees", "fonctionnelle"),
    ("v0.6", "alphaTest + une passe plein ecran en moins", "fonctionnelle"),
    ("v0.7", "lumiere teintee, eau animee, ciel etoile", "fonctionnelle"),
    ("v0.8", "ombres reactivees, bloom demi-res, brume", "ombres buggees"),
    ("v0.8.1", "ombres retirees, bloom demi-res, brume", "SEULE VERSION ENTIEREMENT FONCTIONNELLE"),
]


def load_manifests():
    packs = []
    root = os.path.join(BASE, "packs")
    if not os.path.isdir(root):
        return packs
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "manifest.json")
        if os.path.isfile(p):
            try:
                packs.append(json.load(open(p, encoding="utf-8")))
            except (OSError, ValueError):
                pass
    return packs


def main():
    packs = load_manifests()
    packs.sort(key=lambda m: (m.get("project_type", ""), m.get("slug", "")))

    lines = []
    lines.append("# Registre des projets - FliflightMC")
    lines.append("")
    lines.append(f"Genere le {date.today().isoformat()} par `scripts/gen_project_registry.py` "
                 "- **ne pas editer a la main**.")
    lines.append("")
    lines.append(f"{len(packs)} projets dans le pipeline `packs/`. Les binaires ne sont pas dans le "
                 "depot : ils sont attaches aux **GitHub Releases** (voir `publish.py`).")
    lines.append("")
    lines.append("## Projets publies (pipeline `packs/`)")
    lines.append("")
    lines.append("| Projet | Type | CurseForge | Modrinth | Version |")
    lines.append("|---|---|---|---|---|")
    for m in packs:
        name = (m.get("name") or m.get("slug", "")).replace("|", "/")
        cf = m.get("curseforge_id")
        mr = m.get("modrinth_id")
        ver = (m.get("version") or {}).get("number", "")
        cf_l = f"[{cf}](https://www.curseforge.com/projects/{cf})" if cf else "-"
        mr_l = f"[{mr}](https://modrinth.com/project/{mr})" if mr else "-"
        lines.append(f"| {name} | {m.get('project_type', '-')} | {cf_l} | {mr_l} | {ver} |")
    lines.append("")

    lines.append("## Shader pack (`shaderpacks/fliflight-vanilla-plus/`)")
    lines.append("")
    lines.append("Hors pipeline : pas encore publie sur CurseForge / Modrinth (decision : plus tard).")
    lines.append("Cible Minecraft Java 1.21.x, OptiFine / Iris. Profil **Potato**.")
    lines.append("")
    lines.append("| Version | Contenu | Etat |")
    lines.append("|---|---|---|")
    for ver, content, status in SHADER_HISTORY:
        mark = "**" if "SEULE" in status else ""
        lines.append(f"| {mark}{ver}{mark} | {content} | {mark}{status}{mark} |")
    lines.append("")
    lines.append("### Effets actifs dans la version livree (v0.8.1)")
    lines.append("")
    lines.append("Aucun brouillard, bloom (2 passes, buffer demi-resolution), feuillage qui ondule, "
                 "eau animee, lumiere teintee (torches chaudes / ciel froid), lumiere directionnelle, "
                 "ciel avec halo solaire et lunaire + etoiles + bande d'aube, brume d'horizon, "
                 "etalonnage par heure.")
    lines.append("")
    lines.append("### Non livre : les ombres")
    lines.append("")
    lines.append("Trois tentatives, trois artefacts differents. La cause racine de la v0.8 etait reelle "
                 "et prouvee (dans une passe d'ombre `gl_ModelViewMatrix` est la matrice d'ombre, donc "
                 "`gbufferModelViewInverse` dessus donne une position monde absurde), mais le symptome "
                 "suivant - ombres buggees dans un perimetre autour du joueur et clignotantes - n'est "
                 "pas explique. Retirees du zip : OptiFine ne fait donc aucune passe d'ombre.")
    lines.append("")
    lines.append("Pistes non testees, documentees dans le README du pack : distorsion non uniforme de "
                 "`shadowProjection` centree sur le joueur (BSL la compense des deux cotes), et "
                 "l'uniform `shadowFade` ignore.")
    lines.append("")
    lines.append("## Mods Fabric (`mods/`)")
    lines.append("")
    for d in sorted(os.listdir(os.path.join(BASE, "mods"))) if os.path.isdir(os.path.join(BASE, "mods")) else []:
        lines.append(f"- `{d}`")
    lines.append("")

    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"PROJECTS.md ecrit : {os.path.getsize(OUT)} octets, {len(packs)} projets")


if __name__ == "__main__":
    main()
