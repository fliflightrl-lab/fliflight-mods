#!/usr/bin/env python3
"""Generate the test sheet (Markdown + standalone HTML) for the 8 new packs."""
import json, os, glob, html as htmlmod

BASE = r"C:\Users\user\fliflight-mods"
PACKS = os.path.join(BASE, "packs")

CF_ID = {
    "fliflight-low-shield": (1716894, "low-shield-shield-out-of-the-way"),
    "fliflight-no-vignette": (1716909, "no-vignette-clear-screen-corners"),
    "fliflight-clear-water": (1716911, "clear-water-see-through-water"),
    "fliflight-clear-lava": (1716914, "clear-lava-see-through-lava"),
    "fliflight-clear-spyglass": (1716918, "clear-spyglass-no-scope-overlay"),
    "fliflight-clean-hotbar": (1716921, "clean-hotbar-flat-minimal-hud"),
    "fliflight-thin-totem": (1716922, "thin-totem-slimmer-totem-pop"),
    "fliflight-clear-powder-snow": (1716925, "clear-powder-snow-no-frost-overlay"),
}
MR_ID = {
    "fliflight-low-shield": "3kHplXd9",
    "fliflight-no-vignette": "JYyEzln5",
    "fliflight-clear-water": "4KyMcPC1",
    "fliflight-clear-lava": "eG9N5405",
    "fliflight-clear-spyglass": "HEAEl6k5",
    "fliflight-clean-hotbar": "PDnvunp5",
    "fliflight-thin-totem": "32hlofGi",
    "fliflight-clear-powder-snow": "fQlGVRS8",
}

# what to look for in-game, per pack
TESTS = {
    "fliflight-low-shield": [
        "Prends un bouclier dans la main ou l'offhand, passe en vue 1re personne.",
        "Le bouclier doit être NETTEMENT plus petit et plus bas (45 % plus petit).",
        "Bloque (clic droit) : le centre de l'écran doit rester dégagé.",
        "⛔ Si le bouclier est toujours aussi gros ou a disparu → cassé.",
    ],
    "fliflight-no-vignette": [
        "Regarde les 4 coins de l'écran, de jour ET de nuit.",
        "Aucun assombrissement dans les coins (l'écran est uniforme).",
        "⛔ Si les coins restent sombres → cassé. Si l'écran est tout noir → cassé.",
    ],
    "fliflight-clear-water": [
        "Plonge dans l'eau et regarde vers le bas.",
        "Tu dois VOIR le fond (sable/gravats) et les mobs à travers l'eau.",
        "Sous l'eau, le voile bleu plein écran doit avoir disparu.",
        "⛔ Si l'eau est toujours opaque → cassé. Si l'eau a totalement disparu → cassé.",
    ],
    "fliflight-clear-lava": [
        "Place-toi au-dessus d'une flaque de lave et regarde dedans.",
        "La lave doit être semi-transparente (on voit le netherrack dessous).",
        "⛔ Si la lave est toujours opaque → cassé. Si la lave est invisible → cassé.",
    ],
    "fliflight-clear-spyglass": [
        "Prends une longue-vue et utilise-la (clic droit).",
        "Aucun masque noir de viseur : la vue est dégagée sur tout l'écran.",
        "⛔ Si le cercle noir est toujours là → cassé.",
    ],
    "fliflight-clean-hotbar": [
        "Regarde ta barre d'objets en bas (nécessite 1.21.3+).",
        "Fond plat et sobre, 9 cases visibles, cadre fin et clair.",
        "La barre d'XP doit être vert vif et nette.",
        "⛔ Si la barre reste l'ancienne → cassé (vérifie ta version de MC).",
    ],
    "fliflight-thin-totem": [
        "Pop un totem (ou regarde-le dans l'inventaire).",
        "Le totem doit être nettement plus fin (7 px de large au lieu de 16).",
        "⛔ Si le totem est coupé au milieu ou invisible → cassé.",
    ],
    "fliflight-clear-powder-snow": [
        "Entre dans de la poudreuse et reste dedans jusqu'à geler.",
        "Aucun voile de givre sur les bords de l'écran.",
        "⛔ Si le givre est toujours là → cassé.",
    ],
}

rows = []
for slug, (cfid, cfslug) in CF_ID.items():
    m = json.load(open(os.path.join(PACKS, slug, "manifest.json"), encoding="utf-8"))
    zips = glob.glob(os.path.join(PACKS, slug, "files", "*.zip"))
    zip_name = os.path.basename(zips[0]) if zips else "(zip manquant)"
    rows.append({
        "slug": slug,
        "name": m["name"],
        "summary": m["summary"],
        "zip": zip_name,
        "zip_path": zips[0] if zips else "",
        "cf": f"https://www.curseforge.com/minecraft/texture-packs/{cfslug}",
        "cf_id": cfid,
        "mr": f"https://modrinth.com/resourcepack/{slug}",
        "mr_id": MR_ID[slug],
        "tests": TESTS[slug],
    })

# ---------------------------------------------------------------- MARKDOWN
md = ["# 🧪 Test des 8 nouveaux packs — Fliflight",
      "",
      "**Comment tester :** copie les 8 zips depuis `~/fliflight-mods/dist/` dans ton dossier "
      "`%appdata%\\.minecraft\\resourcepacks\\`, puis **active UN pack à la fois** (sinon tu ne verras pas "
      "quelle modification fait quoi).",
      "",
      "> 💡 Les 8 zips sont aussi dans `packs/<slug>/files/`.",
      "",
      "---",
      ""]
for i, r in enumerate(rows, 1):
    md.append(f"## {i}. {r['name']}")
    md.append("")
    md.append(f"*{r['summary']}*")
    md.append("")
    md.append(f"- **Zip à tester :** `{r['zip']}`")
    md.append(f"- **Dossier local :** `{r['zip_path']}`")
    md.append(f"- **CurseForge :** {r['cf']}")
    md.append(f"- **Modrinth :** {r['mr']}")
    md.append("")
    md.append("**À vérifier en jeu :**")
    for t in r["tests"]:
        md.append(f"- [ ] {t}")
    md.append("")
    md.append("**Résultat :** `[ ] OK`   `[ ] CASSÉ`   détail : ______________")
    md.append("")
    md.append("---")
    md.append("")
md.append("## 📋 Récap à me renvoyer")
md.append("")
md.append("| # | Pack | OK ? | Problème constaté |")
md.append("|---|---|---|---|")
for i, r in enumerate(rows, 1):
    md.append(f"| {i} | {r['name']} | ☐ | |")
md.append("")

md_path = os.path.join(BASE, "TEST-8-PACKS.md")
open(md_path, "w", encoding="utf-8").write("\n".join(md))
print("wrote", md_path)

# ---------------------------------------------------------------- HTML
def esc(s):
    return htmlmod.escape(s or "")

cards = []
for i, r in enumerate(rows, 1):
    tests = "".join(f"<li>{esc(t)}</li>" for t in r["tests"])
    cards.append(f"""
  <section class="card">
    <header>
      <span class="num">{i}</span>
      <h2>{esc(r['name'])}</h2>
    </header>
    <p class="sum">{esc(r['summary'])}</p>
    <ul class="tests">{tests}</ul>
    <div class="links">
      <a href="{esc(r['cf'])}" target="_blank">CurseForge</a>
      <a href="{esc(r['mr'])}" target="_blank">Modrinth</a>
    </div>
    <div class="file"><code>{esc(r['zip'])}</code></div>
    <div class="verdict">
      <label><input type="checkbox"> OK</label>
      <label><input type="checkbox"> CASSÉ</label>
      <input class="note" type="text" placeholder="détail du problème…">
    </div>
  </section>""")

html_doc = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Test des 8 nouveaux packs — Fliflight</title>
<style>
  :root{
    --bg:#0e1016; --card:#161a23; --line:#262c3a; --fg:#e8eaf0; --mut:#98a0b3;
    --acc:#5cc8ff; --ok:#5cd68a; --bad:#ff6b6b;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);
       font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
  .wrap{max-width:1080px;margin:0 auto;padding:40px 20px 80px}
  h1{font-size:30px;margin:0 0 6px}
  .intro{color:var(--mut);margin:0 0 8px}
  .how{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--acc);
       border-radius:10px;padding:14px 18px;margin:24px 0 34px;color:#cfd4e0;font-size:14px}
  .how code{background:#0b0d12;padding:2px 6px;border-radius:5px;color:var(--acc);font-size:13px}
  .grid{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(330px,1fr))}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 18px 16px;
        display:flex;flex-direction:column;gap:10px}
  .card header{display:flex;align-items:center;gap:10px}
  .num{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:8px;
       background:#0b0d12;border:1px solid var(--line);color:var(--acc);font-size:13px;font-weight:600;flex:none}
  .card h2{font-size:16px;margin:0;line-height:1.3}
  .sum{color:var(--mut);font-size:13.5px;margin:0}
  .tests{margin:2px 0 0;padding-left:18px;font-size:13.5px;color:#d5d9e4}
  .tests li{margin:4px 0}
  .tests li::marker{color:var(--acc)}
  .links{display:flex;gap:14px;font-size:13px;margin-top:2px}
  .links a{color:var(--acc);text-decoration:none;border-bottom:1px solid rgba(92,200,255,.35)}
  .links a:hover{border-bottom-color:var(--acc)}
  .file code{display:block;background:#0b0d12;border:1px solid var(--line);border-radius:7px;
             padding:6px 9px;font-size:12px;color:#9fb4cd;overflow-wrap:anywhere}
  .verdict{display:flex;gap:12px;align-items:center;margin-top:auto;padding-top:10px;border-top:1px dashed var(--line)}
  .verdict label{display:flex;align-items:center;gap:6px;font-size:13px;color:#cfd4e0;white-space:nowrap}
  .verdict input[type=checkbox]{accent-color:var(--acc);width:15px;height:15px}
  .verdict .note{flex:1;min-width:0;background:#0b0d12;border:1px solid var(--line);border-radius:7px;
                 padding:6px 9px;color:var(--fg);font-size:13px;font-family:inherit}
  footer{margin-top:40px;color:var(--mut);font-size:13px}
</style></head>
<body><div class="wrap">
  <h1>🧪 Test des 8 nouveaux packs</h1>
  <p class="intro">Coche OK / CASSÉ pour chaque pack et note le problème — je corrige derrière.</p>
  <div class="how">
    <strong>Comment tester :</strong> copie les 8 zips depuis <code>~/fliflight-mods/dist/</code> vers
    <code>%appdata%\\.minecraft\\resourcepacks\\</code>, puis active <strong>un pack à la fois</strong>
    (sinon impossible de voir quelle modif fait quoi). Les zips sont aussi dans <code>packs/&lt;slug&gt;/files/</code>.
  </div>
  <div class="grid">__CARDS__
  </div>
  <footer>Généré depuis <code>~/fliflight-mods/scripts/gen_test_sheet.py</code> — 8 packs v1.0.0, build 1.21.4.</footer>
</div></body></html>"""

html_path = os.path.join(BASE, "TEST-8-PACKS.html")
open(html_path, "w", encoding="utf-8").write(html_doc.replace("__CARDS__", "".join(cards)))
print("wrote", html_path)

# copy the zips into a single convenient folder
test_dir = os.path.join(BASE, "dist", "TESTEZ-MOI")
os.makedirs(test_dir, exist_ok=True)
for r in rows:
    if r["zip_path"] and os.path.exists(r["zip_path"]):
        import shutil
        shutil.copy2(r["zip_path"], os.path.join(test_dir, r["zip"]))
print("copied zips ->", test_dir)
print(len(os.listdir(test_dir)), "files")
