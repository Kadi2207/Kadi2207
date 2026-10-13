"""Génère les SVG du profil (charte sombre bleu nuit et doré) et l'en-tête des README des 3 dépôts de projets.

Usage, depuis la racine du dépôt :
    python scripts/build_svgs.py --fonts <dossier>                   (tout le profil)
    python scripts/build_svgs.py --fonts <dossier> hero contact      (cibles choisies)
    python scripts/build_svgs.py --fonts <dossier> entetes           (assets/header.svg des 3 dépôts voisins)
Cibles : hero flow contact chips footer cards captures building entetes.
Le pied de page (footer) n'est pas régénéré par défaut : il garde son dessin actuel.

Polices (licence SIL Open Font License 1.1, voir assets/POLICES.md) :
- Playfair Display (Claus Eggers Sørensen) : titres, nom, chiffres ; paquet npm @fontsource/playfair-display 5.3.0
- Source Sans 3 (Paul D. Hunt, Adobe) : texte courant ; paquet npm @fontsource/source-sans-3 5.3.0
Pour les obtenir, dans un dossier vide : npm pack <paquet> --ignore-scripts, puis tar -xzf du .tgz ;
regrouper les .woff des deux dossiers package/files dans <dossier>. Le texte est converti en tracés :
les SVG ne chargent aucune police et ne contiennent pas les fichiers de police.

Les SVG sont servis via <img> : pas de script, pas de ressource externe. Chacun porte son fond bleu nuit
(rendu identique en clair et sombre). Textes : animation jouée une seule fois, finie avant 4 s. Bannière, flow
et contact : décor (et étapes du flow) en boucle douce de 18 s, avec une pause sur l'état final entre deux
cycles. L'état de base de chaque SVG est son état final (lisible sans animation) et prefers-reduced-motion
coupe tout, boucle comprise.
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

# Charte bleu nuit (passe finale, harmonisée avec la bannière LinkedIn)
NAVY, CARD, NAVY_HI = "#0f2038", "#172b4c", "#152a4b"  # fond ; cartes (bleu un peu plus clair) ; centre du dégradé de la bannière
INK, MUTED = "#e8eef5", "#b7c3d3"  # texte clair ; texte secondaire (> 7:1 sur NAVY et CARD)
FIL = AMP = "#C9953B"  # doré : filets, losanges, « & »
BEIGE, CREME = "#F6E8CC", "#FBF4E4"  # accents seulement (filets, contours, citation), jamais en fond plein
BAND, BEIGE_LIGHT = NAVY, INK  # alias de l'ancienne charte
# Charte sombre des grands panneaux (bannière, flow, contact) et des chips, d'après les maquettes du 2026-10-13
DARK, DARK2, DARK_HI = "#0a1422", "#0d1b2a", "#14283f"  # fond profond ; fond des panneaux ; halo
GLOW = "#E2BD72"  # doré clair : reflet du trait et particules
SOFT = "#a9bcd6"  # bleu clair des sous-titres (> 8:1 sur DARK2)
NOMOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
W = 1000

# Animations jouées une seule fois (la boucle douce est définie plus bas). Sans animation, l'état de base est l'état final.
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
# particules qui scintillent une fois ; onde de la pastille « Disponible » (état final et de base : invisible)
ANIM2 = ANIM + (
    "@keyframes tw{from{opacity:0}50%{opacity:1;transform:scale(2)}}"
    "@keyframes ping{from{opacity:.9;transform:scale(1)}to{opacity:0;transform:scale(3)}}"
    ".tw{transform-box:fill-box;transform-origin:center;animation:tw .8s ease-out backwards}"
    ".ping{transform-box:fill-box;transform-origin:center;animation:ping 1.2s ease-out backwards}"
    ".grow{transform-box:fill-box;transform-origin:center}"
)

# Boucle douce : cycle de 18 s, animations finies vers 10 s au plus tard, pause sur l'état final, puis retour à
# l'état de départ pendant les RESET dernières secondes. Chaque élément en boucle reçoit ses propres @keyframes
# (style en ligne, qui remplace l'animation de sa classe) ; prefers-reduced-motion les coupe (animation:none).
CYCLE, RESET = 18.0, 0.8
# type : (état de départ, [(fraction de la durée, état intermédiaire)], état final, accélération)
ETATS = {
    "up": ("opacity:0;transform:translateY(18px)", [], "opacity:1;transform:none", "cubic-bezier(.2,.7,.2,1)"),
    "fade": ("opacity:0", [], "opacity:1", "ease-out"),
    "draw": ("stroke-dashoffset:1", [], "stroke-dashoffset:0", "cubic-bezier(.45,0,.2,1)"),
    "lz": ("opacity:0;transform:scale(.2) rotate(-90deg)", [(.6, "opacity:1;transform:scale(1.35)")], "opacity:1;transform:none", "ease-out"),
    "tw": ("opacity:0", [(.5, "opacity:1;transform:scale(2)")], "opacity:1;transform:none", "ease-out"),
    "ping": ("opacity:0", [(0, "opacity:.9;transform:scale(1)")], "opacity:0;transform:scale(3)", "ease-out"),
    "lit": ("opacity:.35", [], "opacity:1", "ease-out"),  # étape du flow : atténuée puis allumée
    "grow": ("transform:scale(0)", [], "transform:none", "cubic-bezier(.3,.6,.3,1)"),  # losange du flow qui se remplit
}
DUREES = {"up": 1.0, "fade": .9, "draw": 1.1, "lz": .6, "tw": .8, "ping": 1.2, "lit": .6, "grow": .7}
KF = {}


def boucle(cls, delay, dur=None):
    """Attributs d'un élément en boucle : classe (transform-box, dasharray) et animation propre de CYCLE secondes."""
    dur = dur or DUREES[cls]
    name = f"{cls}_{round(delay * 100)}_{round(dur * 100)}"
    if name not in KF:
        pre, mids, end, ease = ETATS[cls]
        fr = [(0, pre, "" if delay > 0 else ease)]
        if delay > 0:
            fr.append((delay - (.01 if mids and mids[0][0] == 0 else 0), pre, ease))
        fr += [(delay + f * dur, st, ease) for f, st in mids]
        fr += [(delay + dur, end, ""), (CYCLE - RESET, end, "ease-in-out"), (CYCLE, pre, "")]

        def pc(t):
            return (f"{t / CYCLE * 100:.3f}".rstrip("0").rstrip(".") or "0") + "%"

        KF[name] = f"@keyframes {name}{{" + "".join(
            f"{pc(t)}{{{st}{f';animation-timing-function:{ez}' if ez else ''}}}" for t, st, ez in fr) + "}"
    return f' class="{cls}" style="animation:{name} {num(CYCLE)}s linear infinite"'


def kf_css():
    """@keyframes des éléments en boucle du SVG en cours, puis remise à zéro."""
    s = "".join(KF.values())
    KF.clear()
    return s


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


def anim(cls, delay, dur=None, loop=False):
    if loop:
        return boucle(cls, delay, dur)
    return f' class="{cls}" style="animation-delay:{delay:.2f}s{f";animation-duration:{dur}s" if dur else ""}"'


def diamond(cx, cy, r, ry=None):
    ry = r if ry is None else ry
    return f"M{num(cx)} {num(cy - ry)}L{num(cx + r)} {num(cy)}L{num(cx)} {num(cy + ry)}L{num(cx - r)} {num(cy)}Z"


def lz(cx, cy, r, delay, fill=FIL, ry=None, loop=False):
    return f'<path{anim("lz", delay, loop=loop)} fill="{fill}" d="{diamond(cx, cy, r, ry)}"/>'


def rule(x1, y, x2, delay, dur=0.8, width=2.5, color=FIL, opacity=1, loop=False):
    op = f' stroke-opacity="{opacity}"' if opacity != 1 else ""
    return f'<path{anim("draw", delay, dur, loop)} pathLength="1" d="M{num(x1)} {num(y)}H{num(x2)}" stroke="{color}" stroke-width="{width}"{op} fill="none"/>'


def eyebrow(text, x, y, delay=None, size=25, color=MUTED):
    """Petit intitulé en capitales espacées, précédé d'un losange doré."""
    f = font("ss700")
    r = size * 0.24
    g, w = text_g(f, [(text, color)], size, x + 2 * r + size * 0.45, y, tracking=0.14)
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


def ligne_g(fnt, items, size, x, y, anchor, t0, step, color=INK, loop=False, sep=FIL):
    """Éléments sur une ligne, séparés par des ◆ dessinés (absents de la police) qui s'allument à tour de rôle.
    loop : seuls les ◆ sont en boucle, le texte apparaît une fois."""
    r, gap = size * 0.17, size * 0.55
    ws = [fnt.width(m, size) for m in items]
    total = sum(ws) + (len(items) - 1) * (2 * gap + 2 * r)
    cx = x - total / 2 if anchor == "middle" else x
    cy = y - size * fnt.xh / 2
    parts = []
    for i, (m, w) in enumerate(zip(items, ws)):
        parts.append(text_g(fnt, [(m, color)], size, cx, y, cls="fade", style=f"animation-delay:{t0 + i * step:.2f}s")[0])
        cx += w
        if i < len(items) - 1:
            parts.append(lz(cx + gap + r, cy, r, t0 + i * step + step * .6, fill=sep, loop=loop))
            cx += 2 * gap + 2 * r
    return "".join(parts), total


def ligne_w(fnt, items, size):
    return sum(fnt.width(m, size) for m in items) + (len(items) - 1) * size * 2 * (0.55 + 0.17)


# ---------------------------------------------------------------- bannière éditoriale (fond beige « tech », trait doré en arc)
# Fond beige de la bannière et du pied de page (2026-10-13, rappel de la bannière LinkedIn) : texte bleu nuit ; le doré
# #C9953B n'atteint que 2,2:1 sur beige, il reste aux filets et losanges, et le texte d'accent prend un doré foncé.
B_INK, B_MUTED, B_SOFT, B_GOLD = "#0d1b2a", "#3a4b60", "#2c4a6e", "#7a5212"  # 14:1, 7:1, 7,5:1, 5,7:1 sur #F6E8CC
GOLD_DEEP = "#A8741F"  # bout du trait lumineux sur beige (le doré clair #E2BD72 y disparaît)
NOM = "Kadidiatou Bagayoko"
HERO_SOUS = [("Étudiante en Intelligence Artificielle ", B_INK), ("&", B_GOLD), (" Data Science", B_INK)]
HERO_CONTACT = ["Villiers-sur-Marne, France", "kadibaga22@gmail.com", "LinkedIn"]
HERO_PHRASE = "Passionnée par la data et l'IA, je recherche une alternance en Data & IA à partir d'octobre 2026."
CITATION = ["Comprendre le besoin,", "construire la solution,", "livrer l'impact."]


def panel(Wd, H, gid="pn", cx="80%", cy="15%"):
    """Grand panneau sombre à coins arrondis, halo discret, liseré doré : (defs, fond)."""
    defs = (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="95%"><stop offset="0" stop-color="{DARK_HI}"/>'
            f'<stop offset=".5" stop-color="{DARK2}"/><stop offset="1" stop-color="{DARK}"/></radialGradient>')
    bg = (f'<rect width="{Wd}" height="{num(H)}" rx="20" fill="url(#{gid})"/>'
          f'<rect x="1" y="1" width="{Wd - 2}" height="{num(H - 2)}" rx="19" fill="none" stroke="{FIL}" stroke-opacity=".4" stroke-width="1.5"/>')
    return defs, bg


def beige_panel(Wd, H, gid, cx, cy, dx, dy):
    """Grand panneau beige « tech » : dégradé crème → beige, trame de points bleu nuit qui s'estompe autour de (dx, dy),
    halo doré très léger, liseré doré : (defs, fond). Pas d'aplat."""
    defs = (f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="100%"><stop offset="0" stop-color="{CREME}"/>'
            f'<stop offset=".5" stop-color="{BEIGE}"/><stop offset="1" stop-color="#F2E0BE"/></radialGradient>'
            f'<radialGradient id="{gid}h" cx="{dx}" cy="{dy}" r="45%"><stop offset="0" stop-color="{GLOW}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{GLOW}" stop-opacity="0"/></radialGradient>'
            f'<pattern id="{gid}p" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1.2" fill="{B_INK}"/></pattern>'
            f'<radialGradient id="{gid}m" cx="{dx}" cy="{dy}" r="60%"><stop offset="0" stop-color="#fff"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="{gid}k"><rect width="{Wd}" height="{num(H)}" fill="url(#{gid}m)"/></mask>')
    bg = (f'<rect width="{Wd}" height="{num(H)}" rx="20" fill="url(#{gid})"/>'
          f'<rect width="{Wd}" height="{num(H)}" rx="20" fill="url(#{gid}h)"/>'
          f'<rect width="{Wd}" height="{num(H)}" rx="20" fill="url(#{gid}p)" fill-opacity=".1" mask="url(#{gid}k)"/>'
          f'<rect x="1" y="1" width="{Wd - 2}" height="{num(H - 2)}" rx="19" fill="none" stroke="{FIL}" stroke-opacity=".7" stroke-width="1.5"/>')
    return defs, bg


def glow_defs(gid, x1, x2, end=GLOW):
    """Dégradé du trait lumineux (transparent puis doré puis doré clair) et flou de son halo."""
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" x2="{x2}"><stop offset="0" stop-color="{FIL}" stop-opacity="0"/>'
            f'<stop offset=".35" stop-color="{FIL}"/><stop offset="1" stop-color="{end}"/></linearGradient>'
            f'<filter id="{gid}b" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>')


def glow_path(d, gid, t0, dur, width=2.5, loop=False, halo=GLOW):
    """Trait doré qui se trace, doublé d'un halo flou tracé en même temps."""
    return (f'<path{anim("draw", t0, dur, loop)} pathLength="1" d="{d}" fill="none" stroke="{halo}" stroke-width="{width * 3}" stroke-opacity=".45" filter="url(#{gid}b)"/>'
            f'<path{anim("draw", t0, dur, loop)} pathLength="1" d="{d}" fill="none" stroke="url(#{gid})" stroke-width="{width}" stroke-linecap="round"/>')


def sparks(pts, t0, step, loop=False, color=GLOW):
    """Particules dorées discrètes : visibles sans animation, scintillent une fois (ou à chaque cycle)."""
    return "".join(f'<circle{anim("tw", t0 + i * step, loop=loop)} cx="{num(x)}" cy="{num(y)}" r="{r}" fill="{color}" fill-opacity="{op}"/>'
                   for i, (x, y, r, op) in enumerate(pts))


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def hero_svg():
    fn, fr, fq, fm = font("ss600"), font("ss400"), font("pf400i"), font("pf700")
    pad, H = 56, 548
    s_nom = fn.fit(NOM, 80, 860, tracking=.015)
    defs, bg = beige_panel(W, H, "hb", "18%", "12%", "88%", "30%")
    arc = ((-10, 530), (330, 512), (660, 450), (1010, 205))
    defs += glow_defs("ga", 0, W, end=GOLD_DEEP)
    body = [bg]
    # trait lumineux en arc, derrière le texte et l'encadré (en boucle, comme les particules et les losanges)
    body.append(glow_path(f"M{arc[0][0]} {arc[0][1]}C{arc[1][0]} {arc[1][1]} {arc[2][0]} {arc[2][1]} {arc[3][0]} {arc[3][1]}", "ga", .3, 2.3, loop=True, halo=FIL))
    pts = []
    for k, (t, dy, r, op) in enumerate(((.18, -14, 1.6, .7), (.31, 9, 1.2, .6), (.44, -22, 2, .8), (.55, 12, 1.4, .6), (.63, -8, 2.4, .9),
                                         (.74, 18, 1.3, .6), (.83, -26, 1.8, .8), (.9, 6, 2.6, .9), (.96, -16, 1.4, .7))):
        x, y = bezier(*arc, t)
        pts.append((x, y + dy, r, op))
    pts += [(912, 72, 1.6, .55), (958, 128, 1.1, .5), (842, 40, 1.2, .45), (720, 96, 1, .4)]
    body.append(sparks(pts, 1.4, .1, loop=True, color=FIL))
    # nom, filet doré prolongé d'un filet fin bleu nuit, sous-titre, coordonnées (◆ dorés), phrase
    body.append(text_g(fn, [(NOM, B_INK)], s_nom, pad, 132, tracking=.015, cls="up", style="animation-delay:.1s")[0])
    body.append(rule(pad, 162, pad + 120, .55, .7, 2.5, loop=True))
    body.append(lz(pad + 134, 162, 5, 1.05, loop=True))
    body.append(rule(pad + 148, 162, pad + 196, 1.2, .5, 1.2, color=B_SOFT, opacity=.5, loop=True))
    body.append(text_g(fr, HERO_SOUS, 33, pad, 218, cls="fade", style="animation-delay:.7s")[0])
    body.append(ligne_g(fr, HERO_CONTACT, 25, pad, 268, "start", 1.0, .15, color=B_SOFT, loop=True, sep=FIL)[0])
    svg, last = para(fr, HERO_PHRASE, 30, pad, 340, 500, 42, color=B_INK)
    body.append(f'<g{anim("fade", 1.3)}>{svg}</g>')
    # encadré citation à droite
    x0, y0, bw, bh = 598, 292, 346, 190
    q = [f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bh}" rx="14" fill="{DARK2}" stroke="{FIL}" stroke-opacity=".6" stroke-width="1.5"/>',
         text_g(fm, [("“", FIL)], 64, x0 + 26, y0 + 70)[0]]
    q += [text_g(fq, [(ln, CREME)], 28, x0 + 30, y0 + 84 + i * 38)[0] for i, ln in enumerate(CITATION)]
    q.append(f'<path d="M{x0 + 70} {y0 + 36}H{x0 + 130}" stroke="{BEIGE}" stroke-opacity=".7" stroke-width="1.5"/>')
    q.append(f'<path fill="{FIL}" d="{diamond(x0 + bw - 24, y0 + bh - 24, 6, 8)}"/>')
    body.append(f'<g{anim("up", 1.6)}>{"".join(q)}</g>')
    desc = (f"{NOM}. Étudiante en Intelligence Artificielle & Data Science. " + ", ".join(HERO_CONTACT) + ". "
            + HERO_PHRASE + " Citation : " + " ".join(CITATION))
    return svg_v2(W, H, NOM, desc, defs, "\n".join(body), style=ANIM2 + kf_css()), dict(nom=s_nom, sous_titre=33, coordonnees=25, phrase=30, citation=28)


# ---------------------------------------------------------------- pied de page : vague beige « tech » (comme la bannière), filet doré, losanges
def footer_svg():
    H = 130

    def wy(x):
        return 54 - 18 * math.sin(2 * math.pi * (x - 250) / 1000)

    xs = list(range(0, W + 1, 50))
    top = smooth([(x, wy(x)) for x in xs])
    fil_r = smooth([(x, wy(x) + 16) for x in xs if x >= 500])
    fil_l = smooth([(x, wy(x) + 16) for x in reversed(xs) if x <= 500])
    fil_b = smooth([(x, wy(x) + 26) for x in xs])
    defs = (
        f'<linearGradient id="bg" x1="0" x2="1"><stop offset="0" stop-color="#F2E0BE"/><stop offset=".5" stop-color="{CREME}"/>'
        f'<stop offset="1" stop-color="#F2E0BE"/></linearGradient>'
        f'<pattern id="pt" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="11" cy="11" r="1.2" fill="{B_INK}"/></pattern>'
        f'<clipPath id="cp"><rect width="{W}" height="{H}" rx="20"/></clipPath>'
    )
    body = [f'<g clip-path="url(#cp)"><path d="{top}V{H}H0Z" fill="url(#bg)"/><path d="{top}V{H}H0Z" fill="url(#pt)" fill-opacity=".08"/></g>']
    body.append(f'<path{anim("draw", .5, 1.4)} pathLength="1" d="{fil_b}" fill="none" stroke="{B_SOFT}" stroke-opacity=".45" stroke-width="1"/>')
    for d in (fil_l, fil_r):
        body.append(f'<path{anim("draw", .2, 1.4)} pathLength="1" d="{d}" fill="none" stroke="{FIL}" stroke-width="2"/>')
    body.append(lz(500, wy(500) + 16, 8, .15, ry=10))
    for k, x in enumerate((250, 750)):
        body.append(lz(x, wy(x) + 16, 5, .8 + k * .1))
    for k, dx in enumerate((-26, 0, 26)):
        body.append(lz(500 + dx, 104, 4.5 if dx else 6, 1.4 + k * .12, fill=B_INK if dx == 0 else FIL))
    return svg_v2(W, H, "Pied de page", "Bandeau décoratif : vague beige, filet doré, filet bleu nuit et losanges.", defs, "\n".join(body))


# ---------------------------------------------------------------- schéma « Du besoin à la solution » (fil d'or vertical)
FLOW_TITRE = "Du besoin à la solution"
FLOW_SOUS = "à travers des stratégies digitales innovantes"
ETAPES = [
    ("Besoin", "Analyse des processus et recommandations présentées au Consul (Consulat du Mali)"),
    ("Nettoyage", "397 884 lignes de transactions nettoyées (e-commerce), audit qualité de 5 234 contacts (RevOps)"),
    ("Modèle / analyse", "TF-IDF + Random Forest (TCIM), LLMs via l'API Hugging Face (WMDP)"),
    ("Dashboard", "Streamlit + Plotly, KPIs et reporting pour la direction"),
]


def flow_svg():
    ft, fs, fi, fnum = font("ss700"), font("pf400i"), font("ss400"), font("ss700")
    pad, xl, xt = 56, 92, 148
    st, si, lh = 38, 29, 39
    maxw = W - xt - pad
    # en-tête : ◆ titre, puis la phrase d'étape
    r = 46 * 0.24
    title = f'<path fill="{FIL}" d="{diamond(pad + r, 96 - 46 * ft.cap / 2, r, r * 1.25)}"/>' + text_g(ft, FLOW_TITRE, 46, pad + 2 * r + 20, 96)[0]
    body_head = [f'<g{anim("up", .1)}>{title}</g>',
                 text_g(fs, [(FLOW_SOUS, BEIGE)], 31, pad + 2 * r + 20, 146, cls="fade", style="animation-delay:.6s")[0],
                 rule(pad, 184, W - pad, .9, .7, 1.2, opacity=.45)]
    y = 250
    nodes, centers = [], []
    for k, (titre, ligne) in enumerate(ETAPES):
        yt = y
        centers.append(yt - st * ft.cap / 2)
        parts = [text_g(ft, titre, st, xt, yt)[0]]
        svg, last = para(fi, ligne.replace(" (", " ("), si, xt, yt + 46, maxw, lh, color=MUTED)
        parts.append(svg)
        nodes.append(parts)
        y = last + 78
    H = y - 78 + 56
    defs, bg = panel(W, H, "fb", cx="15%", cy="0%")
    body = [bg] + body_head
    # rail discret, toujours visible ; puis, en boucle et une étape à la fois : le fil d'or rejoint l'étape, elle
    # s'allume (texte et contour), son losange se remplit d'or, une coche beige la valide. Pause : 4 étapes validées.
    rn = 24
    body.append(f'<path d="M{xl} {num(centers[0])}V{num(centers[-1])}" stroke="{FIL}" stroke-opacity=".25" stroke-width="2" fill="none"/>')
    t0, pas = 1.3, 2.2
    for k, (c, parts) in enumerate(zip(centers, nodes)):
        t = t0 + k * pas
        if k:
            body.append(f'<path{anim("draw", t - .6, .6, True)} pathLength="1" d="M{xl} {num(centers[k - 1] + rn)}V{num(c - rn)}" stroke="{FIL}" stroke-width="3" fill="none"/>')
        body.append(f'<path fill="{DARK2}" d="{diamond(xl, c, rn)}"/>')
        body.append(f'<path{anim("lit", t, .5, True)} fill="none" stroke="{FIL}" stroke-width="2.5" d="{diamond(xl, c, rn)}"/>')
        body.append(f'<path{anim("grow", t + .4, .7, True)} fill="{FIL}" d="{diamond(xl, c, rn - 5)}"/>')
        body.append(f'<g{anim("fade", t + .8, .4, True)}>{text_g(fnum, [(str(k + 1), DARK)], 22, xl, c + 22 * fnum.cap / 2, anchor="middle")[0]}</g>')
        body.append(f'<g{anim("lit", t + .05, .6, True)}>{"".join(parts)}</g>')
        bx, by = xl + 21, c - 21
        body.append(f'<circle{anim("fade", t + 1.1, .4, True)} cx="{num(bx)}" cy="{num(by)}" r="11" fill="{DARK}" stroke="{BEIGE}" stroke-width="1.8"/>')
        body.append(f'<path{anim("draw", t + 1.25, .5, True)} pathLength="1" d="M{num(bx - 5)} {num(by + .5)}L{num(bx - 1.5)} {num(by + 4)}L{num(bx + 5.5)} {num(by - 4)}"'
                    f' fill="none" stroke="{BEIGE}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    desc = (f"{FLOW_TITRE}, {FLOW_SOUS}. Quatre étapes reliées par un fil d'or, validées l'une après l'autre. "
            + " ".join(f"{k + 1}, {t} : {l}." for k, (t, l) in enumerate(ETAPES)))
    return svg_v2(W, H, FLOW_TITRE, desc, defs, "\n".join(body), style=ANIM2 + kf_css()), dict(titre=46, etape=st, texte=si)


# ---------------------------------------------------------------- contact (grand panneau, ligne dorée ondulée)
CONTACT_TITRE = [("Construisons quelque chose d'", INK), ("utile.", FIL)]
CONTACT_SOUS = "Ouverte aux opportunités en Data, Machine Learning et IA"
CONTACT_BLOCS = [("linkedin", "LinkedIn", "linkedin.com/in/kadi-bagayoko"), ("email", "Email", "kadibaga22@gmail.com"), ("github", "GitHub", "github.com/Kadi2207")]


def contact_icon(kind, cx, cy, s=34):
    h = s / 2
    st = f'fill="none" stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"'
    if kind == "linkedin":  # carré arrondi + « in » (le logo LinkedIn n'est pas dans simple-icons)
        g, w = text_g(font("ss700"), [("in", INK)], s * .62, cx, cy + s * .62 * font("ss700").cap / 2 + 1, anchor="middle")
        return f'<rect x="{num(cx - h)}" y="{num(cy - h)}" width="{s}" height="{s}" rx="6" {st}/>' + g
    if kind == "email":
        return (f'<rect x="{num(cx - h)}" y="{num(cy - h * .72)}" width="{s}" height="{num(s * .72)}" rx="4" {st}/>'
                f'<path d="M{num(cx - h + 2)} {num(cy - h * .72 + 3)}L{num(cx)} {num(cy + 2)}L{num(cx + h - 2)} {num(cy - h * .72 + 3)}" {st}/>')
    sc = s / 24
    return f'<g transform="translate({num(cx - h)} {num(cy - h)}) scale({round(sc, 3)})"><path d="{icon_path(kind)}" fill="{INK}"/></g>'


def arrow(x, y, s=14):
    return f'<path d="M{num(x)} {num(y + s)}L{num(x + s)} {num(y)}M{num(x + 3)} {num(y)}H{num(x + s)}V{num(y + s - 3)}" fill="none" stroke="{FIL}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'


def contact_svg():
    fe, ft, fs, fl, fh = font("ss700"), font("ss700"), font("ss400"), font("ss600"), font("ss400")
    pad, H = 56, 540
    defs, bg = panel(W, H, "cb", cx="85%", cy="100%")
    defs += glow_defs("gw", 0, W)
    body = [bg]
    # en-tête : ◆ CONTACT / ÉCHANGEONS, filet, pastille « Disponible »
    r = 24 * 0.26
    g1, w1 = text_g(fe, [("CONTACT", INK), ("  /  ", FIL), ("ÉCHANGEONS", FIL)], 24, pad + 2 * r + 16, 80, tracking=.2)
    body.append(f'<g{anim("fade", .1)}><path fill="{FIL}" d="{diamond(pad + r, 80 - 24 * fe.cap / 2, r, r * 1.25)}"/>{g1}</g>')
    pt, ps = "Disponible", 23
    pw = 20 + 12 + 12 + fl.width(pt, ps) + 20
    px, py, ph = W - pad - pw, 80 - 24 * fe.cap / 2 - 20, 40
    x_rule0 = pad + 2 * r + 16 + w1 + 24
    body.append(rule(x_rule0, 80 - 24 * fe.cap / 2, px - 20, .3, .9, 1.4, opacity=.6, loop=True))
    dot = (px + 26, py + ph / 2)
    body.append(f'<g{anim("fade", .5)}><rect x="{num(px)}" y="{num(py)}" width="{num(pw)}" height="{ph}" rx="{ph / 2}" fill="{DARK}" stroke="{BEIGE}" stroke-opacity=".8" stroke-width="1.5"/>'
                f'<circle cx="{num(dot[0])}" cy="{num(dot[1])}" r="6" fill="{FIL}"/>'
                + text_g(fl, [(pt, CREME)], ps, px + 44, py + ph / 2 + ps * fl.cap / 2)[0] + "</g>")
    for t in (1.0, 2.0):
        body.append(f'<circle{anim("ping", t, loop=True)} cx="{num(dot[0])}" cy="{num(dot[1])}" r="6" fill="none" stroke="{FIL}" stroke-width="2" opacity="0"/>')
    # titre et sous-titre
    s_t = ft.fit(CONTACT_TITRE, 64, W - 2 * pad)
    body.append(text_g(ft, CONTACT_TITRE, s_t, pad, 186, cls="up", style="animation-delay:.3s")[0])
    body.append(text_g(fs, [(CONTACT_SOUS, SOFT)], 30, pad, 238, cls="fade", style="animation-delay:.7s")[0])
    # trois blocs
    gap, y0, bh = 20, 282, 108
    bw = (W - 2 * pad - 2 * gap) / 3
    for i, (kind, label, handle) in enumerate(CONTACT_BLOCS):
        x = pad + i * (bw + gap)
        sh = fh.fit(handle, 21, bw - 78 - 16)
        g = (f'<rect x="{num(x)}" y="{y0}" width="{num(bw)}" height="{bh}" rx="18" fill="{DARK}" fill-opacity=".7" stroke="{FIL}" stroke-opacity=".75" stroke-width="1.5"/>'
             + contact_icon(kind, x + 42, y0 + bh / 2)
             + text_g(fl, [(label, INK)], 29, x + 78, y0 + 50)[0]
             + text_g(fh, [(handle, MUTED)], sh, x + 78, y0 + 82)[0]
             + arrow(x + bw - 34, y0 + 22))
        body.append(f'<g{anim("up", 1.0 + i * .15)}>{g}</g>')
    # ligne dorée ondulée, onde secondaire, points et losanges

    def wy(x, a=1.0, ph=0.0):
        return 468 + a * (16 * math.sin(2 * math.pi * x / 520 + ph) + 9 * math.sin(2 * math.pi * x / 230 + 1.3 + ph))

    xs = list(range(-20, W + 41, 40))
    body.append(f'<path{anim("draw", .9, 2.0, True)} pathLength="1" d="{smooth([(x, wy(x, .7, 1.9) + 10) for x in xs])}" fill="none" stroke="{BEIGE}" stroke-opacity=".35" stroke-width="1.3"/>')
    body.append(glow_path(smooth([(x, wy(x)) for x in xs]), "gw", .9, 2.2, width=2.2, loop=True))
    pts = [(x, wy(x), rr, op) for x, rr, op in ((140, 2.4, .8), (300, 1.6, .6), (470, 2.8, .9), (600, 1.6, .6), (760, 2.4, .8), (880, 1.8, .7))]
    pts += [(x, wy(x, .7, 1.9) + 10, 1.4, .5) for x in (220, 540, 820)]
    body.append(sparks(pts, 1.8, .14, loop=True))
    for k, x in enumerate((380, 930)):
        body.append(lz(x, wy(x), 6, 2.4 + k * .3, ry=8, loop=True))
    desc = ("Construisons quelque chose d'utile. " + CONTACT_SOUS + ". Disponible. "
            + " ".join(f"{l} : {h}." for _, l, h in CONTACT_BLOCS))
    return svg_v2(W, H, "Contact", desc, defs, "\n".join(body), style=ANIM2 + kf_css()), dict(titre=s_t, sous_titre=30, bloc=29, adresse=21)


# ---------------------------------------------------------------- chips (badges locaux, lisibles sur fond blanc et sombre)
# style : « plein » (doré, texte bleu nuit), « point » (contour doré + point doré), « contour » ; icône simple-icons ou None
CHIPS_DISPO = [
    ("dispo", "Disponibilité octobre 2026", "plein"),
    ("alternance", "Alternance 2026-2027 · à partir d'octobre", "point"),
    ("major", "Major de promo B2 2025-2026 · ECE Paris", "point"),
]
CHIPS_COMPETENCES = [("ml", "Machine Learning"), ("genai", "GenAI"), ("python", "Python"), ("sql", "SQL"), ("data-analysis", "Data Analysis")]
STACK = [
    ("Data", [("python", "Python"), (None, "SQL"), ("pandas", "pandas"), (None, "matplotlib"), ("plotly", "Plotly"), ("streamlit", "Streamlit")]),
    ("IA / ML", [(None, "TF-IDF + Random Forest"), ("huggingface", "API Hugging Face")]),
    ("Dév", [("jupyter", "Notebooks"), ("claude", "Claude Code"), ("wordpress", "WordPress")]),
    ("Outils", [("hubspot", "HubSpot (compte gratuit)"), (None, "AWS (Cloud Foundations)")]),
]


def icon_path(name):
    s = (ASSETS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', s).group(1)


def slug(s):
    s = s.lower().replace("é", "e").replace("+", " ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def chip_svg(label, style="contour", icon=False):
    """Pastille de 30 px de haut (texte de 15 px), fond opaque : même rendu sur GitHub clair et sombre."""
    f = font("ss600")
    H, size, padx = 30, 15, 13
    lead = 14 if style == "point" else 0 if icon is False else 22
    w = round(padx + lead + f.width(label, size) + padx + 1)
    fill, stroke, ink = (FIL, FIL, DARK) if style == "plein" else (DARK2, FIL, INK)
    parts = [f'<rect x=".75" y=".75" width="{w - 1.5}" height="{H - 1.5}" rx="{(H - 1.5) / 2}" fill="{fill}" stroke="{stroke}" stroke-opacity=".85" stroke-width="1.5"/>']
    if style == "point":
        parts.append(f'<circle cx="{padx + 4}" cy="{H / 2}" r="4" fill="{FIL}"/>')
    elif icon:
        parts.append(f'<g transform="translate({padx} {H / 2 - 8}) scale({16 / 24:.4f})"><path d="{icon_path(icon)}" fill="{INK}"/></g>')
    elif icon is None:
        parts.append(f'<path fill="{FIL}" d="{diamond(padx + 7, H / 2, 5, 6.5)}"/>')
    parts.append(text_g(f, [(label, ink)], size, padx + lead, H / 2 + size * f.cap / 2)[0])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {H}" width="{w}" height="{H}" role="img" aria-labelledby="t">\n'
            f'<title id="t">{e(label)}</title>\n{"".join(parts)}\n</svg>\n')


def chips():
    d = ASSETS / "chips"
    d.mkdir(exist_ok=True)
    out = []
    for name, label, style in CHIPS_DISPO:
        out.append((f"chips/{name}.svg", chip_svg(label, style)))
    for name, label in CHIPS_COMPETENCES:
        out.append((f"chips/{name}.svg", chip_svg(label)))
    for _, items in STACK:
        for icon, label in items:
            out.append((f"chips/stack-{slug(label)}.svg", chip_svg(label, icon=icon)))
    for fname, s in out:
        write(ASSETS / fname, s)
    return [(f, s, {}) for f, s in out]


# ---------------------------------------------------------------- cartes de projets (texte seul, chiffres dans les phrases)
def card_svg(title, tag, sentences, stack_txt, desc):
    ft, fb = font("pf700"), font("ss400")
    pad, sb, lhb = 44, 36, 48
    y_tag = pad + 22
    y_title = y_tag + 68
    parts = [eyebrow(tag.upper(), pad, y_tag, delay=.1, size=24, color=BEIGE)[0]]
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
    _, bg = frame(W, H, fill=DARK2)
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
    parts = [eyebrow("EN CONSTRUCTION", pad, y, delay=.1, size=24, color=BEIGE)[0]]
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
    grad, bg = frame(W, H, fill=DARK2)
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
    # charte sombre du profil (comme le flow et le contact) : panneau à halo et liseré doré, texte clair,
    # filet doré centré avec losange, petits losanges beige en accent, quelques particules dorées
    defs, bg = panel(W, H, "eb", cx="50%", cy="0%")
    defs += (
        f'<linearGradient id="fl" gradientUnits="userSpaceOnUse" x1="{W / 2 - 180}" x2="{W / 2 + 180}"><stop offset="0" stop-color="{FIL}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{GLOW}"/><stop offset="1" stop-color="{FIL}" stop-opacity="0"/></linearGradient>'
    )
    body = [bg, f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="12" fill="none" stroke="{FIL}" stroke-opacity=".3"/>']
    body.append(text_g(ft, [(nom, INK)], s, W / 2, 128, anchor="middle", cls="up", style="animation-delay:.1s")[0])
    for x2 in (W / 2 - 180, W / 2 + 180):
        body.append(f'<path{anim("draw", .5)} pathLength="1" d="M{W / 2} 168H{num(x2)}" stroke="url(#fl)" stroke-width="2" fill="none"/>')
    body.append(lz(W / 2, 168, 7, .45, ry=9))
    for k, x in enumerate((W / 2 - 200, W / 2 + 200)):
        body.append(lz(x, 168, 3.5, .9 + k * .1, fill=BEIGE, ry=4.5))
    body.append(sparks([(W / 2 - 330, 62, 1.6, .5), (W / 2 + 300, 48, 2, .6), (W / 2 + 360, 176, 1.3, .45), (W / 2 - 280, 190, 1.2, .4)], 1.1, .12))
    return svg_v2(W, H, nom, f"En-tête : {nom}.", defs, "\n".join(body), style=ANIM2), dict(titre=s)


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
    ap.add_argument("cibles", nargs="*", help="hero flow contact chips footer cards captures building entetes (défaut : tout le profil sauf footer)")
    ap.add_argument("--fonts", required=True, help="dossier des .woff de @fontsource/playfair-display et @fontsource/source-sans-3")
    ap.add_argument("--apercu", help="chemin d'une page HTML d'aperçu de tous les SVG, à garder hors du dépôt")
    a = ap.parse_args()
    for key, fname in FONT_FILES.items():
        FONTS[key] = Font(Path(a.fonts) / f"{fname}.woff")
    simples = {
        "hero": ("hero.svg", hero_svg), "flow": ("flow.svg", flow_svg), "contact": ("contact.svg", contact_svg),
        "footer": ("footer.svg", lambda: (footer_svg(), {})), "building": ("building.svg", building_svg),
    }
    cibles = a.cibles or [c for c in simples if c != "footer"] + ["chips", "cards", "captures"]
    built = []
    for c in cibles:
        if c in simples:
            fname, fn = simples[c]
            s, m = fn()
            write(ASSETS / fname, s)
            built.append((fname, s, m))
        elif c == "chips":
            built += chips()
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
