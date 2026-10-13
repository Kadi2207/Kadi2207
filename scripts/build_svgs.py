"""Génère les SVG animés du profil (charte bleu nuit) et l'en-tête des README des 3 dépôts de projets.

Usage, depuis la racine du dépôt :
    python scripts/build_svgs.py --fonts <dossier>                   (tout le profil)
    python scripts/build_svgs.py --fonts <dossier> hero footer       (cibles choisies)
    python scripts/build_svgs.py --fonts <dossier> entetes           (assets/header.svg des 3 dépôts voisins)
Cibles : hero disponibilite footer flow idcard stack cards captures building entetes.

Polices (licence SIL Open Font License 1.1, voir assets/POLICES.md) :
- Playfair Display (Claus Eggers Sørensen) : titres, nom, chiffres ; paquet npm @fontsource/playfair-display 5.3.0
- Source Sans 3 (Paul D. Hunt, Adobe) : texte courant ; paquet npm @fontsource/source-sans-3 5.3.0
Pour les obtenir, dans un dossier vide : npm pack <paquet> --ignore-scripts, puis tar -xzf du .tgz ;
regrouper les .woff des deux dossiers package/files dans <dossier>. Le texte est converti en tracés :
les SVG ne chargent aucune police et ne contiennent pas les fichiers de police.

Les SVG sont servis via <img> : pas de script, pas de ressource externe. Chacun porte son fond bleu nuit
(rendu identique en clair et sombre). Animations jouées une seule fois, finies avant 4 s ; l'état de
base de chaque SVG est son état final (lisible sans animation) et prefers-reduced-motion les coupe.
Lisibilité mobile : largeur de 1000 unités, affichée vers 328 px sur un téléphone de 360 px (x 0,33).
"""
import argparse
import base64
import io
import math
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Bande de disponibilité (assets/disponibilite.svg), seul endroit où vit ce texte. Pour régénérer uniquement ce fichier :
#   python scripts/build_svgs.py --fonts <dossier des .woff> disponibilite
STATUT = ("Disponible pour une alternance dès octobre 2026", "Analyse de données, science des données, IA")

# Charte bleu nuit (passe finale, harmonisée avec la bannière LinkedIn)
NAVY, CARD, NAVY_HI = "#0f2038", "#172b4c", "#152a4b"  # fond ; cartes (bleu un peu plus clair) ; centre du dégradé de la bannière
INK, MUTED = "#e8eef5", "#b7c3d3"  # texte clair ; texte secondaire (> 7:1 sur NAVY et CARD)
FIL = AMP = "#C9953B"  # doré : filets, losanges, « & »
BEIGE = "#F6E8CC"  # décor rare
BAND, BEIGE_LIGHT = NAVY, INK  # alias de l'ancienne charte
NOMOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
W = 1000

# Animations : une seule fois, rien d'infini. Sans animation, l'état de base est l'état final.
ANIM = (
    "@keyframes up{from{opacity:0;transform:translateY(18px)}}"
    "@keyframes fade{from{opacity:0}}"
    "@keyframes draw{from{stroke-dashoffset:1}}"
    "@keyframes lz{from{opacity:0;transform:scale(.2) rotate(-90deg)}60%{opacity:1;transform:scale(1.35)}}"
    ".up{animation:up 1s cubic-bezier(.2,.7,.2,1) backwards}"
    ".fade{animation:fade .9s ease-out backwards}"
    ".draw{stroke-dasharray:1;animation:draw 1.1s cubic-bezier(.45,0,.2,1) backwards}"
    ".lz{transform-box:fill-box;transform-origin:center;animation:lz .6s ease-out backwards}"
)


def e(s):
    return escape(s, quote=False)


def write(path, content):
    path = Path(path)
    path.write_text(content, encoding="utf-8")
    print("ok", path.relative_to(ROOT.parent), len(content) // 1024, "Ko")


# ---------------------------------------------------------------- texte en tracés
def num(v):
    s = f"{v:.1f}"
    s = s.rstrip("0").rstrip(".") if "." in s else s
    return "0" if s in ("-0", "") else s


def xadv(v):
    return (getattr(v, "XAdvance", 0) or 0) if v is not None else 0


class Font:
    """Lit un .woff avec fontTools : contours, chasses et crénage GPOS (paires, formats 1 et 2)."""

    def __init__(self, path):
        from fontTools.ttLib import TTFont

        self.f = TTFont(str(path))
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.hmtx = self.f["hmtx"].metrics
        self.xh = self.f["OS/2"].sxHeight / self.upm
        self.cap = self.f["OS/2"].sCapHeight / self.upm
        self.pairs, self.classes, self.subst = {}, [], {}
        if "GSUB" in self.f:  # chiffres alignés (lnum) : Playfair a des chiffres elzéviriens par défaut
            t = self.f["GSUB"].table
            for i in sorted({i for fr in t.FeatureList.FeatureRecord if fr.FeatureTag == "lnum" for i in fr.Feature.LookupListIndex}):
                lk = t.LookupList.Lookup[i]
                for st in lk.SubTable:
                    typ = lk.LookupType
                    if typ == 7:
                        typ, st = st.ExtensionLookupType, st.ExtSubTable
                    if typ == 1:
                        self.subst.update(st.mapping)
        if "GPOS" in self.f:
            t = self.f["GPOS"].table
            idx = sorted({i for fr in t.FeatureList.FeatureRecord if fr.FeatureTag == "kern" for i in fr.Feature.LookupListIndex})
            for i in idx:
                lk = t.LookupList.Lookup[i]
                for st in lk.SubTable:
                    typ = lk.LookupType
                    if typ == 9:
                        typ, st = st.ExtensionLookupType, st.ExtSubTable
                    if typ != 2:
                        continue
                    if st.Format == 1:
                        for g1, ps in zip(st.Coverage.glyphs, st.PairSet):
                            for r in ps.PairValueRecord:
                                self.pairs.setdefault((g1, r.SecondGlyph), xadv(r.Value1))
                    else:
                        self.classes.append((set(st.Coverage.glyphs), st))

    def kern(self, a, b):
        if (a, b) in self.pairs:
            return self.pairs[(a, b)]
        for cov, st in self.classes:
            if a in cov:
                c1 = st.ClassDef1.classDefs.get(a, 0)
                c2 = st.ClassDef2.classDefs.get(b, 0)
                v = xadv(st.Class1Record[c1].Class2Record[c2].Value1)
                if v:
                    return v
        return 0

    def glyph(self, ch):
        g = self.cmap.get(ord(ch))
        if g is None and ch == "\u00a0":
            g = self.cmap.get(32)
        if g is None:
            raise KeyError(f"caractère absent de la police : {ch!r} (U+{ord(ch):04X})")
        return self.subst.get(g, g)

    def shape(self, runs, size, tracking=0.0):
        """runs : [(texte, couleur)]. Renvoie ([(d, couleur)], chasse totale), origine sur la ligne de base."""
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen

        s = size / self.upm
        x, prev, out = 0.0, None, []
        for text, color in runs:
            pen = SVGPathPen(self.gs, ntos=num)
            for ch in text:
                g = self.glyph(ch)
                if prev:
                    x += self.kern(prev, g) * s
                self.gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
                x += self.hmtx[g][0] * s + tracking * size
                prev = g
            out.append((pen.getCommands(), color))
        return out, x - tracking * size

    def width(self, text, size, tracking=0.0):
        runs = text if isinstance(text, list) else [(text, INK)]
        return self.shape(runs, size, tracking)[1]

    def fit(self, text, size, max_w, tracking=0.0):
        w = self.width(text, size, tracking)
        return size if w <= max_w else size * max_w / w


FONTS = {}
FONT_FILES = {
    "pf700": "playfair-display-latin-700-normal",
    "pf600": "playfair-display-latin-600-normal",
    "pf400i": "playfair-display-latin-400-italic",
    "ss400": "source-sans-3-latin-400-normal",
    "ss600": "source-sans-3-latin-600-normal",
    "ss700": "source-sans-3-latin-700-normal",
}


def font(key):
    return FONTS[key]


def typo(s):
    """Typographie française : apostrophe courbe, espaces insécables dans les nombres et avant % : ; ! ?"""
    s = s.replace("'", "\u2019")
    s = re.sub(r"(\d) (?=\d{3}\b)", "\\1\u00a0", s)
    return re.sub(r" (?=[%:;!?])", "\u00a0", s)


def text_g(fnt, runs, size, x, y, anchor="start", tracking=0.0, cls="", style=""):
    runs = [(typo(t), c) for t, c in (runs if isinstance(runs, list) else [(runs, INK)])]
    paths, w = fnt.shape(runs, size, tracking)
    x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
    attrs = (f' class="{cls}"' if cls else "") + (f' style="{style}"' if style else "")
    inner = "".join(f'<path fill="{c}" d="{d}"/>' for d, c in paths if d)
    if attrs:  # une animation CSS sur transform remplacerait l'attribut transform : groupe interne
        inner = f"<g{attrs}>{inner}</g>"
    return f'<g transform="translate({num(x0)} {num(y)})">{inner}</g>', w


def wrap(fnt, text, size, max_w):
    lines, cur = [], ""
    for word in typo(text).split(" "):
        t = f"{cur} {word}" if cur else word
        if cur and fnt.width(t, size) > max_w:
            lines.append(cur)
            cur = word
        else:
            cur = t
    lines.append(cur)
    # pas de mot seul en dernière ligne
    if len(lines) > 1 and " " not in lines[-1] and lines[-2].count(" ") >= 2:
        head, last = lines[-2].rsplit(" ", 1)
        if fnt.width(f"{last} {lines[-1]}", size) <= max_w:
            lines[-2:] = [head, f"{last} {lines[-1]}"]
    return lines


def para(fnt, text, size, x, y, max_w, lh, color=INK, anchor="start"):
    """Paragraphe à la ligne automatique. Renvoie (svg, ordonnée de la dernière ligne de base)."""
    lines = wrap(fnt, text, size, max_w)
    out = [text_g(fnt, [(ln, color)], size, x, y + i * lh, anchor=anchor)[0] for i, ln in enumerate(lines)]
    return "".join(out), y + (len(lines) - 1) * lh


def anim(cls, delay, dur=None):
    return f' class="{cls}" style="animation-delay:{delay:.2f}s{f";animation-duration:{dur}s" if dur else ""}"'


def diamond(cx, cy, r, ry=None):
    ry = r if ry is None else ry
    return f"M{num(cx)} {num(cy - ry)}L{num(cx + r)} {num(cy)}L{num(cx)} {num(cy + ry)}L{num(cx - r)} {num(cy)}Z"


def lz(cx, cy, r, delay, fill=FIL, ry=None):
    return f'<path{anim("lz", delay)} fill="{fill}" d="{diamond(cx, cy, r, ry)}"/>'


def rule(x1, y, x2, delay, dur=0.8, width=2.5, color=FIL, opacity=1):
    op = f' stroke-opacity="{opacity}"' if opacity != 1 else ""
    return f'<path{anim("draw", delay, dur)} pathLength="1" d="M{num(x1)} {num(y)}H{num(x2)}" stroke="{color}" stroke-width="{width}"{op} fill="none"/>'


def eyebrow(text, x, y, delay=None, size=25):
    """Petit intitulé en capitales espacées, précédé d'un losange doré."""
    f = font("ss700")
    r = size * 0.24
    g, w = text_g(f, [(text, MUTED)], size, x + 2 * r + size * 0.45, y, tracking=0.14)
    d = f'<path fill="{FIL}" d="{diamond(x + r, y - size * f.cap / 2, r)}"/>'
    inner = d + g
    if delay is not None:
        inner = f'<g{anim("fade", delay)}>{inner}</g>'
    return inner, 2 * r + size * 0.45 + w


def smooth(pts):
    """Catmull-Rom vers Bézier cubiques."""
    d = f"M{num(pts[0][0])} {num(pts[0][1])}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{num(c1[0])} {num(c1[1])} {num(c2[0])} {num(c2[1])} {num(p2[0])} {num(p2[1])}"
    return d


def frame(Wd, H, fill=CARD, border=True):
    """Fond propre à chaque SVG (rendu identique sur GitHub clair et sombre) : carte bleu nuit à coins arrondis."""
    bg = f'<rect width="{Wd}" height="{num(H)}" rx="20" fill="{fill}"/>'
    if border:
        bg += f'<rect x="1" y="1" width="{Wd - 2}" height="{num(H - 2)}" rx="19" fill="none" stroke="{FIL}" stroke-opacity=".35" stroke-width="1.5"/>'
    return "", bg


def svg_v2(Wd, H, title, desc, defs, body, style=ANIM):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wd} {num(H)}" width="{Wd}" height="{num(H)}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{e(title)}</title>\n<desc id="d">{e(desc)}</desc>\n'
        "<metadata>Texte converti en tracés depuis Playfair Display et Source Sans 3 (SIL Open Font License 1.1).</metadata>\n"
        f"<style>{style}\n{NOMOTION}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n"
    )


def ligne_g(fnt, items, size, x, y, anchor, t0, step):
    """Éléments sur une ligne, séparés par des ◆ dessinés (absents de la police) qui s'allument à tour de rôle."""
    r, gap = size * 0.17, size * 0.55
    ws = [fnt.width(m, size) for m in items]
    total = sum(ws) + (len(items) - 1) * (2 * gap + 2 * r)
    cx = x - total / 2 if anchor == "middle" else x
    cy = y - size * fnt.xh / 2
    parts = []
    for i, (m, w) in enumerate(zip(items, ws)):
        parts.append(text_g(fnt, m, size, cx, y, cls="fade", style=f"animation-delay:{t0 + i * step:.2f}s")[0])
        cx += w
        if i < len(items) - 1:
            parts.append(lz(cx + gap + r, cy, r, t0 + i * step + step * .6))
            cx += 2 * gap + 2 * r
    return "".join(parts), total


def ligne_w(fnt, items, size):
    return sum(fnt.width(m, size) for m in items) + (len(items) - 1) * size * 2 * (0.55 + 0.17)


# ---------------------------------------------------------------- bannière (variante A, permanente : ni statut ni date)
NOM = "Kadidiatou Bagayoko"
METIERS = ["Analyse de données", "Création de dashboards", "Machine learning"]
ACC1 = [("Utiliser la data ", INK), ("&", AMP), (" l’IA", INK)]
ACC2 = [("pour concevoir des solutions innovantes.", INK)]


def hero_svg():
    bold, semi, ital = font("pf700"), font("pf600"), font("pf400i")
    s_nom = bold.fit(NOM, 100, 840)
    s_m = min(40, 40 * 860 / ligne_w(semi, METIERS[:2], 40))
    s_a = ital.fit(ACC2, 38, 860)
    y_nom, fy, ym = 160, 206, 278
    ya = ym + s_m * 1.4 + 70
    H = round(ya + s_a * 1.3 + 92)
    bg = f'<rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>'
    defs = (
        f'<radialGradient id="bg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="{NAVY_HI}"/><stop offset="1" stop-color="{NAVY}"/></radialGradient>'
        f'<linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="{W / 2 - 230}" x2="{W / 2 + 230}"><stop offset="0" stop-color="{FIL}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{FIL}"/><stop offset="1" stop-color="{FIL}" stop-opacity="0"/></linearGradient>'
    )
    body = [bg, f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="12" fill="none" stroke="{FIL}" stroke-opacity=".5"/>']
    for cx, cy in ((16, 16), (W - 16, 16), (16, H - 16), (W - 16, H - 16)):
        body.append(lz(cx, cy, 5, 2.6))
    body.append(text_g(bold, NOM, s_nom, W / 2, y_nom, anchor="middle", cls="up", style="animation-delay:.15s")[0])
    # filet d'or tracé depuis le centre, losanges qui s'allument
    for x2 in (W / 2 - 230, W / 2 + 230):
        body.append(f'<path{anim("draw", .7)} pathLength="1" d="M{num(W / 2)} {fy}H{num(x2)}" stroke="url(#fl)" stroke-width="2" fill="none"/>')
    body.append(lz(W / 2, fy, 9, .65, ry=11))
    for k, dx in enumerate((-40, 40)):
        body.append(lz(W / 2 + dx, fy, 4, 1.0 + k * .08))
    # métiers sur deux lignes (lisibles à 328 px) : le retour à la ligne remplace le second ◆
    body.append(ligne_g(semi, METIERS[:2], s_m, W / 2, ym, "middle", 1.1, .3)[0])
    body.append(ligne_g(semi, METIERS[2:], s_m, W / 2, ym + s_m * 1.4, "middle", 1.7, .3)[0])
    for k, runs in enumerate((ACC1, ACC2)):
        body.append(text_g(ital, runs, s_a, W / 2, ya + k * s_a * 1.3, anchor="middle", cls="fade", style=f"animation-delay:{2.1 + k * .2:.2f}s")[0])
    desc = "Kadidiatou Bagayoko. Analyse de données, création de dashboards, machine learning. Utiliser la data & l'IA pour concevoir des solutions innovantes."
    return svg_v2(W, H, NOM, desc, defs, "\n".join(body)), dict(nom=s_nom, metiers=s_m, accroche=s_a)


# ---------------------------------------------------------------- bande de disponibilité
def disponibilite_svg():
    f1, f2 = font("ss600"), font("ss400")
    size, lh, pad = 36, 50, 34
    r = size * 0.2
    gap = size * 0.5
    w1 = f1.width(STATUT[0], size)
    w2 = f2.width(STATUT[1], size)
    one_line = w1 + 2 * gap + 2 * r + gap + w2 <= W - 80
    top = pad + size * f1.cap
    parts = []
    if one_line:
        x = (W - (w1 + 3 * gap + 2 * r + w2)) / 2
        parts.append(text_g(f1, [(STATUT[0], BEIGE_LIGHT)], size, x, top, cls="up", style="animation-delay:.2s")[0])
        parts.append(lz(x + w1 + gap + r, top - size * f1.xh / 2, r, .9, fill=FIL))
        parts.append(text_g(f2, [(STATUT[1], BEIGE_LIGHT)], size, x + w1 + 2 * gap + 2 * r, top, cls="fade", style="animation-delay:1.1s")[0])
        last = top
    else:
        lines1 = wrap(f1, STATUT[0], size, W - 80)
        for i, ln in enumerate(lines1):
            parts.append(text_g(f1, [(ln, BEIGE_LIGHT)], size, W / 2, top + i * lh, anchor="middle", cls="up", style=f"animation-delay:{.2 + i * .15:.2f}s")[0])
        y2 = top + len(lines1) * lh
        lines2 = wrap(f2, STATUT[1], size, W - 80 - 2 * r - gap)
        for i, ln in enumerate(lines2):
            yy = y2 + i * lh
            w = f2.width(ln, size)
            x = (W - (2 * r + gap + w)) / 2 if i == 0 else (W - w) / 2
            if i == 0:
                parts.append(lz(x + r, yy - size * f2.xh / 2, r, .9, fill=FIL))
                x += 2 * r + gap
            parts.append(text_g(f2, [(ln, BEIGE_LIGHT)], size, x, yy, cls="fade", style=f"animation-delay:{1.1 + i * .15:.2f}s")[0])
        last = y2 + (len(lines2) - 1) * lh
    H = round(last + pad + size * 0.25)
    body = [f'<rect width="{W}" height="{H}" rx="14" fill="{CARD}"/>',
            f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="none" stroke="{FIL}" stroke-opacity=".35" stroke-width="1.5"/>']
    for x2 in (W / 2 - 160, W / 2 + 160):
        body.append(f'<path{anim("draw", .3, 1.0)} pathLength="1" d="M{W / 2} {H - 10}H{num(x2)}" stroke="{FIL}" stroke-width="2" stroke-opacity=".8" fill="none"/>')
    body += parts
    desc = f"{STATUT[0]}. {STATUT[1]}."
    return svg_v2(W, H, "Disponibilité", desc, "", "\n".join(body)), dict(texte=size, lignes="1" if one_line else "2")


# ---------------------------------------------------------------- pied de page : vague beige, filet doré, losanges
def footer_svg():
    H = 130

    def wy(x):
        return 54 - 18 * math.sin(2 * math.pi * (x - 250) / 1000)

    xs = list(range(0, W + 1, 50))
    top = smooth([(x, wy(x)) for x in xs])
    fil_r = smooth([(x, wy(x) + 16) for x in xs if x >= 500])
    fil_l = smooth([(x, wy(x) + 16) for x in reversed(xs) if x <= 500])
    defs = (
        f'<linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset=".5" stop-color="{CARD}"/>'
        f'<stop offset="1" stop-color="{NAVY}"/></linearGradient>'
        f'<clipPath id="cp"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
    )
    body = [f'<g clip-path="url(#cp)"><path d="{top}V{H}H0Z" fill="url(#bg)"/></g>']
    for d in (fil_l, fil_r):
        body.append(f'<path{anim("draw", .2, 1.4)} pathLength="1" d="{d}" fill="none" stroke="{FIL}" stroke-width="2"/>')
    body.append(lz(500, wy(500) + 16, 8, .15, ry=10))
    for k, x in enumerate((250, 750)):
        body.append(lz(x, wy(x) + 16, 5, .8 + k * .1))
    for k, dx in enumerate((-26, 0, 26)):
        body.append(lz(500 + dx, 104, 4.5 if dx else 6, 1.4 + k * .12, fill=BEIGE if dx == 0 else FIL))
    return svg_v2(W, H, "Pied de page", "Bandeau décoratif : vague bleu nuit, filet doré et losanges.", defs, "\n".join(body))


# ---------------------------------------------------------------- schéma « Du besoin à la solution » (fil d'or vertical)
ETAPES = [
    ("Données", ["397 884 lignes de transactions (e-commerce)", "5 234 contacts (RevOps)"]),
    ("Nettoyage", ["Fiabilisation des données (Consulat du Mali)", "Audit qualité avant migration (RevOps)"]),
    ("Modèle ou analyse", ["TF-IDF + Random Forest (TCIM)", "Analyse des processus (Consulat du Mali)", "LLMs via l'API Hugging Face (WMDP)"]),
    ("Dashboard", ["Streamlit + Plotly", "KPIs et reporting pour la direction"]),
]


def flow_svg():
    ft, fi, fnum = font("pf700"), font("ss400"), font("ss700")
    xl, xt, top = 84, 140, 52
    st, si, lh = 40, 31, 41
    maxw = W - xt - 48
    y = top
    nodes, centers = [], []
    for k, (title, items) in enumerate(ETAPES):
        yt = y + st * 0.74
        centers.append(yt - st * ft.cap / 2)
        parts = [text_g(ft, title, st, xt, yt)[0]]
        yi = yt + 50
        for it in items:
            svg, last = para(fi, it.replace(" (", "\u00a0("), si, xt, yi, maxw, lh)
            parts.append(svg)
            yi = last + lh
        nodes.append(parts)
        y = yi - lh + 58
    H = y - 58 + 52
    grad, bg = frame(W, H, fill=NAVY)
    t0, dur = .2, 2.4
    span = centers[-1] - centers[0]
    body = [bg, f'<path{anim("draw", t0, dur)} pathLength="1" d="M{xl} {num(centers[0])}V{num(centers[-1])}" stroke="{FIL}" stroke-width="3" fill="none"/>']
    for k, (c, parts) in enumerate(zip(centers, nodes)):
        t = t0 + dur * (c - centers[0]) / span
        body.append(lz(xl, c, 24, t, fill=NAVY))
        body.append(f'<path{anim("lz", t)} fill="none" stroke="{FIL}" stroke-width="2.5" d="{diamond(xl, c, 24)}"/>')
        body.append(f'<g{anim("fade", t)}>{text_g(fnum, [(str(k + 1), BEIGE_LIGHT)], 24, xl, c + 24 * fnum.cap / 2, anchor="middle")[0]}</g>')
        body.append(f'<g{anim("fade", t + .1)}>{"".join(parts)}</g>')
    desc = "Schéma en quatre étapes reliées par un fil d'or. " + " ".join(f"{k + 1}, {t} : " + ", ".join(i) + "." for k, (t, i) in enumerate(ETAPES))
    return svg_v2(W, H, "Du besoin à la solution", desc, grad, "\n".join(body)), dict(titre=st, texte=si)


# ---------------------------------------------------------------- carte d'identité
IDENTITE = [
    ("RÔLE", "Data & AI Solutions Builder"),
    ("FORMATION", "Bachelor en Intelligence Artificielle (grade Licence), ECE Paris, 2024-2027"),
    ("RECHERCHE", "Alternance à partir d'octobre 2026, 3 semaines en entreprise, 2 semaines à l'école"),
    ("EN COURS", "Partie IA du projet TCIM, portfolio avec assistant IA"),
]


def idcard_svg():
    fv = font("ss400")
    pad, xv, sv, lh = 44, 300, 32, 42
    maxw = W - xv - pad
    y = pad
    rows = []
    for i, (k, v) in enumerate(IDENTITE):
        lines = wrap(fv, v, sv, maxw)
        yb = y + 18 + sv * 0.74
        rows.append((k, lines, yb, y))
        y = yb + (len(lines) - 1) * lh + 30
    H = y + pad - 12
    grad, bg = frame(W, H)
    body = [bg]
    for i, (k, lines, yb, ytop) in enumerate(rows):
        d = .15 + i * .15
        if i:
            body.append(rule(pad, ytop, W - pad, d, .8, 1.2, opacity=.5))
        g = [eyebrow(k, pad, yb, size=26)[0]]
        g += [text_g(fv, ln, sv, xv, yb + j * lh)[0] for j, ln in enumerate(lines)]
        body.append(f'<g{anim("up", d)}>{"".join(g)}</g>')
    desc = "Carte d'identité. " + " ".join(f"{k.capitalize()} : {v}." for k, v in IDENTITE)
    return svg_v2(W, H, "Carte d'identité", desc, grad, "\n".join(body)), dict(libelle=26, valeur=sv)


# ---------------------------------------------------------------- stack à icônes (4 groupes, technologies de FAITS.md)
# icône simple-icons (assets/icons/) ou None : un losange doré remplace l'icône absente du paquet
STACK = [
    ("DATA", [("python", "Python"), ("pandas", "pandas"), (None, "matplotlib"), ("plotly", "Plotly"), ("streamlit", "Streamlit")]),
    ("IA / ML", [(None, "TF-IDF + Random Forest"), ("huggingface", "API Hugging Face")]),
    ("DEV", [("jupyter", "Notebooks"), ("claude", "Claude Code"), ("wordpress", "WordPress")]),
    ("OUTILS", [("hubspot", "HubSpot (compte gratuit)"), (None, "AWS (Cloud Foundations)")]),
]


def icon_path(name):
    s = (ASSETS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', s).group(1)


def stack_svg():
    fl = font("ss600")
    pad, sl, ch, cgap = 44, 30, 66, 14
    y = pad
    parts, n = [], 0
    for gname, chips in STACK:
        yb = y + 26 * 0.74
        parts.append(eyebrow(gname, pad, yb, delay=.1 + n * .06, size=26)[0])
        x, yc = pad, yb + 26
        for key, label in chips:
            lw = fl.width(label, sl)
            cw = 20 + 30 + 14 + lw + 26
            if x + cw > W - pad:
                x, yc = pad, yc + ch + cgap
            if key:
                ico = f'<g transform="translate({num(x + 20)} {num(yc + 18)}) scale(1.25)"><path d="{icon_path(key)}" fill="{INK}"/></g>'
            else:
                ico = f'<path fill="{FIL}" d="{diamond(x + 35, yc + ch / 2, 8, 10)}"/>'
            g = (
                f'<rect x="{num(x)}" y="{num(yc)}" width="{num(cw)}" height="{ch}" rx="{ch / 2}" fill="{NAVY}" stroke="{FIL}" stroke-opacity=".55"/>'
                + ico + text_g(fl, label, sl, x + 64, yc + 44)[0]
            )
            parts.append(f'<g{anim("up", .15 + n * .06)}>{g}</g>')
            x += cw + cgap
            n += 1
        y = yc + ch + 36
    H = y - 36 + pad
    _, bg = frame(W, H)
    desc = "Stack. " + " ".join(f"{g.capitalize()} : " + ", ".join(l for _, l in c) + "." for g, c in STACK)
    return svg_v2(W, H, "Stack", desc, "", bg + "\n" + "\n".join(parts)), dict(libelle=sl)


# ---------------------------------------------------------------- cartes de projets (texte seul, chiffres dans les phrases)
def card_svg(title, tag, sentences, stack_txt, desc):
    ft, fb = font("pf700"), font("ss400")
    pad, sb, lhb = 44, 36, 48
    y_tag = pad + 22
    y_title = y_tag + 68
    parts = [eyebrow(tag.upper(), pad, y_tag, delay=.1, size=24)[0]]
    parts.append(text_g(ft, title, 52, pad, y_title, cls="up", style="animation-delay:.1s")[0])
    parts.append(rule(pad, y_title + 22, pad + 90, .4, .7, 3))
    y = y_title + 22 + 58
    for i, s in enumerate(sentences):
        svg, last = para(fb, s, sb, pad, y, W - 2 * pad, lhb)
        parts.append(f'<g{anim("fade", .5 + i * .15)}>{svg}</g>')
        y = last + lhb + 12
    y += 10
    ey, ew = eyebrow("STACK", pad, y, size=22)
    svg, last = para(font("ss600"), stack_txt, 31, pad + ew + 20, y, W - 2 * pad - ew - 20, 40, color=MUTED)
    parts.append(f'<g{anim("fade", 1.0)}>{ey}{svg}</g>')
    H = last + 18 + pad
    _, bg = frame(W, H)
    return svg_v2(W, H, title, desc, "", bg + "\n" + "\n".join(parts)), dict(texte=sb, titre=52)


CARTES = [
    ("card-dashboard.svg", "Dashboard e-commerce", "Janvier 2026",
     ["Nettoyage et analyse de 397 884 lignes de transactions avec pandas.",
      "Restitution dans un dashboard Streamlit de 6 indicateurs et 6 graphiques, sur un chiffre d'affaires de £8,91 M."],
     "Python, pandas, Streamlit, Plotly",
     "Dashboard e-commerce, janvier 2026. Nettoyage et analyse de 397 884 lignes de transactions avec pandas. Restitution dans un dashboard Streamlit de 6 indicateurs et 6 graphiques, sur un chiffre d'affaires de £8,91 M. Python, pandas, Streamlit, Plotly."),
    ("card-wmdp.svg", "Hackathon WMDP", "Mars 2026, autrice unique",
     ["Conception d'un corpus de 250 prompts adversariaux en 5 types de reformulation.",
      "Évaluation de 6 LLMs open source via l'API Hugging Face, sur 360 requêtes : 0 % de refus sur Llama et Qwen, mesuré par détection de mots-clés."],
     "API Hugging Face",
     "Hackathon WMDP, mars 2026, autrice unique. Conception d'un corpus de 250 prompts adversariaux en 5 types de reformulation. Évaluation de 6 LLMs open source via l'API Hugging Face, sur 360 requêtes : 0 % de refus sur Llama et Qwen, mesuré par détection de mots-clés. API Hugging Face."),
    ("card-revops.svg", "Audit migration CRM", "Données synthétiques",
     ["Audit de qualité de 734 comptes et 5 234 contacts avant une migration Salesforce vers HubSpot.",
      "Travail sur des données synthétiques issues de Kaggle : aucune donnée d'entreprise."],
     "pandas, matplotlib, notebook",
     "Audit migration CRM, données synthétiques. Audit de qualité de 734 comptes et 5 234 contacts avant une migration Salesforce vers HubSpot. Travail sur des données synthétiques issues de Kaggle : aucune donnée d'entreprise. pandas, matplotlib, notebook."),
]


def cards():
    out = []
    for fname, title, tag, sentences, st, desc in CARTES:
        s, m = card_svg(title, tag, sentences, st, desc)
        write(ASSETS / fname, s)
        out.append((fname, s, m))
    return out


# ---------------------------------------------------------------- captures du dashboard dans une carte nette
# (fichier, zone gardée x0, y0, x1, y1) : on retire les titres Streamlit (qui contiennent des emoji) et la barre d'outils
# Plotly ; les graphiques eux-mêmes sont intacts. La légende courte est dans le README (texte réel, traduit en EN).
CAPTURES = [
    ("screens/dashboard-1.png", (85, 190, 1745, 650)),
    ("screens/dashboard-2.png", (85, 160, 1745, 590)),
    ("screens/dashboard-3.png", (25, 150, 1705, 590)),
]


def capture_svg(src, box, out_w=1500):
    from PIL import Image

    im = Image.open(ASSETS / src).convert("RGB").crop(box)
    im = im.resize((out_w, round(im.height * out_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    uri = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    pad = 18
    iw = W - 2 * pad
    ih = iw * im.height / im.width
    H = ih + 2 * pad
    _, bg = frame(W, H)
    body = (bg + f'<clipPath id="c"><rect x="{pad}" y="{pad}" width="{iw}" height="{num(ih)}" rx="10"/></clipPath>'
            f'<image clip-path="url(#c)" href="{uri}" x="{pad}" y="{pad}" width="{iw}" height="{num(ih)}"/>')
    name = Path(src).stem
    return svg_v2(W, H, f"Capture {name}", f"Capture réelle du dashboard e-commerce ({name}).", "", body, style="")


def captures():
    out = []
    for src, box in CAPTURES:
        s = capture_svg(src, box)
        fname = f"capture-{Path(src).stem}.svg"
        write(ASSETS / fname, s)
        out.append((fname, s, {}))
    return out


# ---------------------------------------------------------------- en construction
CHANTIERS = [
    ("TCIM / Skills4Mind", "depuis avril 2026", [
        "Partie IA : classification automatique de données de santé",
        "3 couches (règles, ML, arbitre), accuracy de 82,5 %",
        "RGPD / RBAC, chiffrement Fernet (AES-128 CBC + HMAC-SHA256)",
        "Présentation du projet sur demande",
    ]),
    ("Portfolio + assistant chatbot IA", "en cours", [
        "Développé avec Claude Code",
        "Connecté à une API de modèle de langage",
        "Lien à venir",
    ]),
]


def building_svg():
    ft, fb, fg = font("pf700"), font("ss400"), font("ss600")
    pad, sb, lhb = 44, 30, 40
    r = sb * 0.17
    y = pad + 24 * 0.74
    parts = [eyebrow("EN CONSTRUCTION", pad, y, delay=.1, size=24)[0]]
    y += 30
    d = .25
    for name, tag, lines in CHANTIERS:
        yn = y + 38 * 0.74 + 12
        g = [text_g(ft, name, 38, pad, yn)[0], text_g(fg, [(tag, MUTED)], 26, W - pad, yn, anchor="end")[0]]
        parts.append(f'<g{anim("up", d)}>{"".join(g)}</g>')
        parts.append(rule(pad, yn + 20, pad + 90, d + .3, .7, 3))
        yl = yn + 20 + 48
        for ln in lines:
            d += .12
            svg, last = para(fb, ln, sb, pad + 2 * r + 14, yl, W - 2 * pad - 2 * r - 14, lhb)
            parts.append(f'<g{anim("fade", d + .2)}><path fill="{FIL}" d="{diamond(pad + r, yl - sb * fb.xh / 2, r)}"/>{svg}</g>')
            yl = last + lhb
        y = yl - lhb + 26
        d += .2
    H = y - 26 + pad + 6
    grad, bg = frame(W, H)
    desc = "En construction. " + " ".join(f"{n} ({t}) : " + ". ".join(ls) + "." for n, t, ls in CHANTIERS)
    return svg_v2(W, H, "En construction", desc, grad, bg + "\n" + "\n".join(parts)), dict(texte=sb, titre=38)


# ---------------------------------------------------------------- en-têtes des README des 3 dépôts de projets
ENTETES = [
    ("ecommerce-dashboard-analytics", "Dashboard e-commerce"),
    ("wmdp-cyber", "Hackathon WMDP"),
    ("revops-crm-migration-analysis", "Audit migration CRM"),
]


def entete_svg(nom):
    ft = font("pf700")
    H = 230
    s = ft.fit(nom, 76, 820)
    grad, bg = frame(W, H, border=False)
    defs = grad + (
        f'<linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="{W / 2 - 180}" x2="{W / 2 + 180}"><stop offset="0" stop-color="{FIL}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{FIL}"/><stop offset="1" stop-color="{FIL}" stop-opacity="0"/></linearGradient>'
    )
    body = [bg, f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="12" fill="none" stroke="{FIL}" stroke-opacity=".5"/>']
    body.append(text_g(ft, nom, s, W / 2, 128, anchor="middle", cls="up", style="animation-delay:.1s")[0])
    for x2 in (W / 2 - 180, W / 2 + 180):
        body.append(f'<path{anim("draw", .5)} pathLength="1" d="M{W / 2} 168H{num(x2)}" stroke="url(#fl)" stroke-width="2" fill="none"/>')
    body.append(lz(W / 2, 168, 7, .45, ry=9))
    return svg_v2(W, H, nom, f"En-tête : {nom}.", defs, "\n".join(body)), dict(titre=s)


def entetes():
    for repo, nom in ENTETES:
        d = ROOT.parent / repo / "assets"
        d.mkdir(exist_ok=True)
        write(d / "header.svg", entete_svg(nom)[0])


# ---------------------------------------------------------------- page d'aperçu locale (hors dépôt)
def apercu(path, items, reduce=False):
    def uri(s):
        return "data:image/svg+xml;base64," + base64.b64encode(s.encode("utf-8")).decode()

    blocks = []
    for label, s in items:
        cells = []
        for bgc, theme in (("#ffffff", "clair"), ("#0d1117", "sombre")):
            for w, kind in ((880, "desktop 880 px"), (360, "mobile 360 px")):
                cells.append(
                    f'<figure class="c" style="background:{bgc};width:{w}px;padding:{16 if w == 360 else 0}px;color:{"#1f2328" if theme == "clair" else "#e6edf3"}">'
                    f'<figcaption>{kind}, fond {theme}</figcaption><img src="{uri(s)}" alt="" style="width:100%;display:block"></figure>'
                )
        blocks.append(f'<section><h2>{e(label)}</h2><div class="row">{"".join(cells)}</div></section>')
    html = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Aperçu du profil</title>'
        "<style>body{margin:0;padding:24px;background:#e9e4da;font-family:Segoe UI,Arial,sans-serif;color:#14284B}"
        "h1{font-size:20px;margin:0 0 4px}p{margin:0 0 18px;font-size:14px}h2{font-size:16px;margin:28px 0 10px}"
        ".row{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-start}.c{margin:0;box-sizing:content-box;border:1px solid #d0c8b8;border-radius:6px;overflow:hidden}"
        "figcaption{font-size:12px;padding:6px 0 8px;opacity:.7}button{font:inherit;padding:6px 14px;border:1px solid #14284B;background:#fff;border-radius:4px;cursor:pointer}</style></head><body>"
        "<h1>Aperçu du profil (charte chaude)</h1><p>Images servies en &lt;img&gt;, comme sur GitHub. Mobile : 360 px de large avec 16 px de marge, soit 328 px d'image. "
        '<button onclick="document.querySelectorAll(\'img\').forEach(i=>{const s=i.src;i.src=\'\';i.src=s})">Rejouer les animations</button></p>'
        + "".join(blocks)
        + "</body></html>"
    )
    Path(path).write_text(html, encoding="utf-8")
    print("ok", path)


# ---------------------------------------------------------------- point d'entrée
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cibles", nargs="*", help="hero disponibilite footer flow idcard stack cards captures building entetes (défaut : tout le profil)")
    ap.add_argument("--fonts", required=True, help="dossier des .woff de @fontsource/playfair-display et @fontsource/source-sans-3")
    ap.add_argument("--apercu", help="chemin d'une page HTML d'aperçu de tous les SVG, à garder hors du dépôt")
    a = ap.parse_args()
    for key, fname in FONT_FILES.items():
        FONTS[key] = Font(Path(a.fonts) / f"{fname}.woff")
    simples = {
        "hero": ("hero.svg", hero_svg), "disponibilite": ("disponibilite.svg", disponibilite_svg), "footer": ("footer.svg", lambda: (footer_svg(), {})),
        "flow": ("flow.svg", flow_svg), "idcard": ("card.svg", idcard_svg),
        "stack": ("stack.svg", stack_svg), "building": ("building.svg", building_svg),
    }
    cibles = a.cibles or list(simples) + ["cards", "captures"]
    built = []
    for c in cibles:
        if c in simples:
            fname, fn = simples[c]
            s, m = fn()
            write(ASSETS / fname, s)
            built.append((fname, s, m))
        elif c == "cards":
            built += cards()
        elif c == "captures":
            built += captures()
        elif c == "entetes":
            entetes()
        else:
            ap.error(f"cible inconnue : {c}")
    for fname, _, m in built:
        if m:
            print(f"  {fname} à 328 px :", {k: (round(v * 328 / W, 1) if isinstance(v, (int, float)) else v) for k, v in m.items()})
    if a.apercu:
        items = [(f, s) for f, s, _ in built]
        items += [(f"En-tête {n}", entete_svg(n)[0]) for _, n in ENTETES]
        apercu(a.apercu, items)
