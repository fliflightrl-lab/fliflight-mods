# Versions de jeu à cocher — projet « VisualTwix » (CurseForge)

Vérifié en comparant avec les **vrais fichiers client de Minecraft** (pas de devinette).
Méthode : le pack ne marche sur une version que si **le fichier qu'il remplace existe** dans cette version.

---

## ⚠️ Deux corrections importantes

| Pack | Ce que je t'avais dit | La VÉRITÉ (vérifiée) |
|---|---|---|
| **Clean Hotbar / Clear Red Bar** | 1.21.3 et + | **1.20.2 et +** (le hotbar sprite existe depuis 1.20.2, mêmes dimensions 182×22 jusqu'à 26.3) |
| **Low Shield** | 1.19 et + | **1.21.4 et + SEULEMENT** (voir explication plus bas) |

Et il manquait des versions dans mes listes précédentes : **1.19.1, 1.19.3, 1.20.3, 1.21.2**, ainsi que **toutes les versions récentes 1.21.9 → 26.3** (Minecraft est passé à un versioning annuel, la dernière release est **26.3**).

---

## 📋 Les listes exactes à cocher

### 1) Clear Spyglass · Clear Pumpkin · Clear Powder Snow · Clear Lava · Clear Water
**→ 29 versions** (ces packs ne remplacent que des textures qui existent dans toutes ces versions)

```
1.19, 1.19.1, 1.19.2, 1.19.3, 1.19.4, 1.20, 1.20.1, 1.20.2, 1.20.3, 1.20.4,
1.20.5, 1.20.6, 1.21, 1.21.1, 1.21.2, 1.21.3, 1.21.4, 1.21.5, 1.21.6, 1.21.7,
1.21.8, 1.21.9, 1.21.10, 1.21.11, 26.1, 26.1.1, 26.1.2, 26.2, 26.3
```

### 2) Clean Hotbar / Clear Red Bar
**→ 22 versions** (de 1.20.2 à 26.3 — avant 1.20.2 le hotbar était dans un autre fichier, `gui/widgets.png`)

```
1.20.2, 1.20.3, 1.20.4, 1.20.5, 1.20.6, 1.21, 1.21.1, 1.21.2, 1.21.3, 1.21.4,
1.21.5, 1.21.6, 1.21.7, 1.21.8, 1.21.9, 1.21.10, 1.21.11, 26.1, 26.1.1, 26.1.2,
26.2, 26.3
```

### 3) Totem · Dark Corners
**→ 29 versions** (comme le groupe 1 — texture d'item et texture de vignette, présentes partout)
→ **À corriger aussi** : tu les as déjà réglés mais avec l'ancienne liste (il manque 1.19.1, 1.19.3, 1.20.3, 1.21.2 et 1.21.9 → 26.3).

### 4) Low Shield — ⚠️ seulement 1.21.4 → 26.3
```
1.21.4, 1.21.5, 1.21.6, 1.21.7, 1.21.8, 1.21.9, 1.21.10, 1.21.11, 26.1, 26.1.1,
26.1.2, 26.2, 26.3
```

---

## Pourquoi Low Shield ne marche PAS avant 1.21.4

Le pack remplace `models/item/shield.json`. En **1.21.4**, Mojang a refondu le système de modèles d'items :
- Le fichier vanilla 1.21.4+ contient `gui_light`, `textures`, `display` — **et plus de `parent`**.
- Le fichier vanilla 1.19 → 1.21.3 contenait `parent: "builtin/entity"` **+ `overrides`** (indispensable pour que le bouclier s'affiche en 3D et que les motifs de bannière apparaissent).

Notre fichier a la structure **1.21.4+** (sans `parent`). Donc :
- ✅ 1.21.4 → 26.3 : parfait (structure identique, seule l'échelle/position du bouclier change).
- ❌ Avant 1.21.4 : le bouclier perdrait son rendu 3D et les motifs de bannière.

**Deux solutions** (dis-moi laquelle tu veux) :
1. **Déclarer 1.21.4+** sur CurseForge (simple, honnête — c'est ce que je recommande pour l'instant).
2. **Je fabrique un modèle compatible toutes versions** (avec `parent: builtin/entity` + `overrides`) puis je le teste. Ça permettrait de descendre à 1.19.

---

## 🎁 Bonus : un souci à connaître

Tous les packs déclarent `pack_format: 46` (= 1.21.4). Sur les autres versions, Minecraft affichera le pack comme **« incompatible »** (juste un avertissement — il fonctionne quand même, il faut confirmer à l'activation).

Pour que ça affiche « compatible » partout, il faut ajouter une plage de formats dans `pack.mcmeta` :
```json
{"pack": {"pack_format": 46, "supported_formats": {"min_inclusive": 9, "max_inclusive": 9999}, "description": "..."}}
```
Je peux le faire sur les 9 packs en 2 minutes si tu veux. Ça évite que les gens croient que le pack est cassé.
