"""Validateur statique de shader pack OptiFine/Iris.

Attrape les erreurs qui donnent un ecran noir SILENCIEUX, sans rien afficher :

  1. #version 120 absent du fichier de tete
  2. accolades / parentheses desequilibrees
  3. #include vers un fichier inexistant (OptiFine exige le nom COMPLET avec extension)
  4. litteral flottant malforme genere par concatenation (1.5.0)
  5. /*DRAWBUFFERS:N*/ absent d'un composite* -> ecrase colortex0
  6. varying utilise dans un .fsh mais absent du .vsh correspondant
  7. DECLARATION DE UNIFORM EN DOUBLE dans la chaine d'include
     -> error C1038: declaration of "x" conflicts with previous declaration
  8. sampler d'ombre nomme autrement que `texture`

Usage: python scripts/validate_shader.py <dossier_du_pack>
Return code 0 si OK, 1 si au moins un probleme.
"""

import os
import re
import sys


def collect(root):
    files = {}
    for r, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            rel = os.path.relpath(p, root).replace("\\", "/")
            if rel.endswith((".glsl", ".vsh", ".fsh", ".properties")):
                try:
                    files[rel] = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    pass
    return files


def expand(rel, files, seen=None):
    """Retourne le texte d'un fichier + tous ses #include resolus (avec sa provenance)."""
    seen = seen or set()
    if rel in seen or rel not in files:
        return ""
    seen.add(rel)
    txt = files[rel]
    out = txt
    for inc in re.findall(r'#include\s+"([^"]+)"', txt):
        target = "shaders/" + inc.lstrip("/")
        out += "\n" + expand(target, files, seen)
    return out


def declared_uniforms(rel, files):
    """{nom: (fichier, ligne)} pour chaque `uniform <type> <nom>;` de la chaine d'include."""
    found = {}
    seen = set()

    def walk(r):
        if r in seen or r not in files:
            return
        seen.add(r)
        for i, line in enumerate(files[r].splitlines(), 1):
            m = re.match(r"\s*uniform\s+(?:lowp |mediump |highp )?\w+\s+(\w+)\s*(\[[^\]]*\])?\s*;", line)
            if m:
                found.setdefault(m.group(1), (r, i))
            if line.lstrip().startswith("#include"):
                inc = re.search(r'"([^"]+)"', line)
                if inc:
                    walk("shaders/" + inc.group(1).lstrip("/"))

    walk(rel)
    return found


def find_functions(code):
    """Retourne [(nom, corps)] pour chaque definition de fonction."""
    out = []
    for m in re.finditer(r"\b(\w+)\s*\([^;{)]*\)\s*\{", code):
        start = m.end() - 1
        depth, i = 0, start
        while i < len(code):
            if code[i] == "{":
                depth += 1
            elif code[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append((m.group(1), code[start:i + 1]))
    return out


DECL = re.compile(r"\b(vec[234]|ivec[234]|float|int|bool|mat[234])\s+(\w+)\s*[=;]")


def duplicate_locals(body):
    """Noms declares deux fois a la MEME profondeur d'accolade dans un meme corps.

    GLSL 1.20 interdit de redeclarer un nom dans la meme portee : c'est une erreur
    de compilation. Un generateur qui emet N fois `vec3 s = ...` au lieu d'appeler
    une fonction tombe exactement la-dedans."""
    seen = {}
    dup = []
    depth = 0
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for m in DECL.finditer(stripped):
            key = (depth, m.group(2))
            if key in seen:
                dup.append(f"{m.group(2)} (profondeur {depth}, deja declare)")
            seen[key] = True
        depth += stripped.count("{") - stripped.count("}")
    return dup


def strip_comments(t):
    """Retire commentaires // et /* */ : le preprocesseur GLSL les ignore, donc compter
    des parentheses dans du texte de commentaire produit des faux positifs."""
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def validate(root):
    files = collect(root)
    problems = []

    for rel, txt in files.items():
        if rel.endswith((".vsh", ".fsh")):
            if not txt.lstrip().startswith("#version 120"):
                problems.append(f"{rel}: ne commence pas par #version 120")
        code = strip_comments(txt)
        if code.count("{") != code.count("}"):
            problems.append(f"{rel}: accolades desequilibrees ({code.count('{')} / {code.count('}')})")
        if code.count("(") != code.count(")"):
            problems.append(f"{rel}: parentheses desequilibrees ({code.count('(')} / {code.count(')')})")
        for inc in re.findall(r'#include\s+"([^"]+)"', txt):
            if not os.path.exists(os.path.join(root, "shaders", inc.lstrip("/"))):
                problems.append(f"{rel}: #include introuvable -> {inc} (l'extension est obligatoire)")
        for bad in re.findall(r"\b\d+\.\d+\.\d+\b", code):
            problems.append(f"{rel}: litteral flottant malforme '{bad}' (concatenation a corriger)")
        for fname, body in find_functions(code):
            for d in duplicate_locals(body):
                problems.append(f"{rel}: dans {fname}() variable locale redeclaree -> {d}")

    for rel in files:
        if re.match(r"shaders/composite\d*\.fsh$", rel) and "DRAWBUFFERS" not in files[rel]:
            problems.append(f"{rel}: pas de /*DRAWBUFFERS:N*/ -> ecraserait colortex0")

    vary = lambda t: set(re.findall(r"varying\s+\w+\s+(\w+)\s*;", t))
    pairs = [(f"shaders/{n}.vsh", f"shaders/{n}.fsh")
             for n in ("shadow", "composite", "composite1", "composite2", "composite3",
                       "composite4", "composite5", "final")]
    pairs += [(f"shaders/gbuffers_{p}.vsh", f"shaders/gbuffers_{p}.fsh")
              for p in ("basic", "line", "textured", "textured_lit", "terrain", "water",
                        "entities", "entities_glowing", "hand", "hand_water", "block",
                        "clouds", "weather", "skybasic", "skytextured", "damagedblock",
                        "beaconbeam", "armor_glint", "spidereyes")]
    for vsh, fsh in pairs:
        if vsh in files and fsh in files:
            missing = vary(expand(fsh, files)) - vary(expand(vsh, files))
            if missing:
                problems.append(f"{fsh}: varying(s) absent(s) du {os.path.basename(vsh)} -> {missing}")

    # 7. uniform declare deux fois dans la meme chaine d'include
    for rel in files:
        if not rel.endswith((".vsh", ".fsh")):
            continue
        seen, dup = set(), []

        def walk(r, first):
            if r in seen or r not in files:
                return
            seen.add(r)
            for i, line in enumerate(files[r].splitlines(), 1):
                m = re.match(r"\s*uniform\s+(?:lowp |mediump |highp )?\w+\s+(\w+)\s*(\[[^\]]*\])?\s*;", line)
                if m:
                    name = m.group(1)
                    if name in first and first[name][0] != r:
                        dup.append(f"{name} ({r}:{i} vs {first[name][0]}:{first[name][1]})")
                    first.setdefault(name, (r, i))
                if line.lstrip().startswith("#include"):
                    inc = re.search(r'"([^"]+)"', line)
                    if inc:
                        walk("shaders/" + inc.group(1).lstrip("/"), first)

        walk(rel, {})
        for d in dup:
            problems.append(f"{rel}: uniform declare DEUX fois -> {d} (error C1038)")

    # 8. programme d'ombre : le sampler doit s'appeler `texture`
    for prog in ("shadow",):
        rel = f"shaders/{prog}.fsh"
        if rel in files:
            for m in re.finditer(r"uniform\s+sampler2D\s+(\w+)\s*;", files[rel]):
                if m.group(1) != "texture":
                    problems.append(f"{rel}: sampler '{m.group(1)}' -> dans un programme d'ombre "
                                    f"OptiFine attend 'texture'")

    return files, problems


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.isdir(root):
        print(f"dossier introuvable: {root}")
        return 1
    files, problems = validate(root)
    glsl = [f for f in files if f.endswith((".glsl", ".vsh", ".fsh"))]
    print(f"{len(glsl)} fichiers GLSL, {len(files) - len(glsl)} autres")
    print(f"PROBLEMES: {len(problems)}")
    for p in problems:
        print("  !!", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
