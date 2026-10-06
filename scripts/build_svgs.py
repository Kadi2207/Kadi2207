"""Génère les SVG animés du profil : hero, carte d'identité, stack, cartes de projets, bloc en construction, schéma.

Usage, depuis la racine du dépôt : python scripts/build_svgs.py
Les SVG sont servis via <img> : pas de script, pas de ressource externe. Les images des cartes
sont intégrées en base64. L'état de base de chaque SVG est son état final (lisible sans animation).
"""
import base64
import io
import re
from html import escape
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

NAVY, NAVY2, GOLD = "#1e3a5f", "#2c5282", "#c8901a"
TEXT, LIGHT, LINE = "#2c3e50", "#f5f8fc", "#c9d6e6"
SANS = "'Segoe UI', Calibri, Arial, sans-serif"
MONO = "Consolas, 'Courier New', monospace"
NOMOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def e(s):
    return escape(s, quote=False)


def svg(w, h, title, desc, style, body, extra_ns=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"{extra_ns} '
        f'viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-labelledby="t d">\n'
        f'<title id="t">{e(title)}</title>\n<desc id="d">{e(desc)}</desc>\n'
        f"<style>{style}\n{NOMOTION}</style>\n{body}\n</svg>\n"
    )


def write(name, content):
    (ASSETS / name).write_text(content, encoding="utf-8")
    print("ok", name, len(content) // 1024, "Ko")


# ---------------------------------------------------------------- hero (terminal)
def hero():
    fs, cw, x0, step = 21, 12.6, 48, 33
    rows = [
        ("cmd", "whoami"),
        ("out", "Kadidiatou Bagayoko · Data & AI Solutions Builder", "#ffffff"),
        ("cmd", "cat recherche.txt"),
        ("out", "Alternance septembre 2026, 3 semaines en entreprise, 2 semaines à l'école", "#e6edf5"),
        ("cmd", "cat consulat_du_mali.txt"),
        ("out", "Analyse des processus, fiabilisation des données, réduction de 50 % des déplacements", "#e6edf5"),
        ("cmd", "cat tcim.txt"),
        ("out", "Partie IA de TCIM : classification de données de santé, accuracy 82,5 %.", "#e6edf5"),
        ("cmd", "cat signature.txt"),
        ("out", "Les données racontent une histoire, je la traduis.", GOLD),
        ("prompt", ""),
    ]
    y = 100
    t = 0.7
    css, body, alltext = [], [], []
    for i, r in enumerate(rows):
        kind = r[0]
        if kind == "cmd":
            y += 10 if i else 0
        txt = ("$ " + r[1]) if kind == "cmd" else r[1] if kind == "out" else "$ "
        n = len(txt)
        w = n * cw
        assert x0 + w < 1160, (txt, x0 + w)
        dur = max(0.4, n * 0.03)
        if kind == "cmd":
            tsp = f'<tspan fill="{GOLD}">$ </tspan><tspan fill="#ffffff">{e(r[1])}</tspan>'
        elif kind == "out":
            tsp = f'<tspan fill="{r[2]}"{" font-weight=\"700\"" if r[2] == "#ffffff" else ""}>{e(r[1])}</tspan>'
        else:
            tsp = f'<tspan fill="{GOLD}">$ </tspan>'
        if kind != "prompt":
            body.append(
                f'<text x="{x0}" y="{y}" font-size="{fs}" textLength="{w:.1f}" lengthAdjust="spacing" xml:space="preserve">{tsp}</text>'
            )
            alltext.append(txt)
            css.append(
                f"@keyframes c{i}{{from{{transform:scaleX(1)}}to{{transform:scaleX(0)}}}}"
                f"@keyframes k{i}{{from{{opacity:1;transform:translateX(0)}}to{{opacity:1;transform:translateX({w:.1f}px)}}}}"
                f".c{i}{{animation:c{i} {dur:.2f}s steps({n},end) {t:.2f}s backwards}}"
                f".k{i}{{animation:k{i} {dur:.2f}s steps({n},end) {t:.2f}s}}"
            )
            body.append(
                f'<rect class="cv c{i}" x="{x0 - 2}" y="{y - fs}" width="{w + 8:.1f}" height="{fs + 9}" fill="{NAVY}"/>'
                f'<rect class="cu k{i}" x="{x0}" y="{y - fs + 2}" width="9" height="{fs + 3}" fill="{GOLD}"/>'
            )
            t += dur + (0.15 if kind == "cmd" else 0.55)
        else:
            cx = x0 + w
            css.append(
                f"@keyframes show{{from{{opacity:0}}to{{opacity:1}}}}@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
                f".pw{{animation:show .01s linear {t:.2f}s backwards}}.pb{{animation:blink 1.06s steps(1) {t:.2f}s infinite}}"
            )
            body.append(
                f'<g class="pw"><text x="{x0}" y="{y}" font-size="{fs}" textLength="{w:.1f}" lengthAdjust="spacing" xml:space="preserve">{tsp}</text><rect class="pb" x="{cx:.1f}" y="{y - fs + 2}" width="9" height="{fs + 3}" fill="{GOLD}"/></g>'
            )
        y += step
    h = y + 22
    style = (
        f"text{{font-family:{MONO}}}.cv{{transform-box:fill-box;transform-origin:100% 50%;transform:scaleX(0)}}"
        ".cu{opacity:0}" + "".join(css)
    )
    bar = (
        f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{NAVY2}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>'
        f'<rect width="1200" height="{h}" rx="14" fill="{NAVY}"/>'
        f'<path d="M0 14a14 14 0 0 1 14-14h1172a14 14 0 0 1 14 14v30H0z" fill="#17304f"/>'
        f'<rect y="44" width="1200" height="3" fill="url(#g)"/>'
        f'<circle cx="28" cy="23" r="6" fill="{GOLD}"/><circle cx="50" cy="23" r="6" fill="#7fa3d1"/><circle cx="72" cy="23" r="6" fill="#b9cbe3"/>'
        f'<text x="600" y="28" font-size="14" text-anchor="middle" fill="#b9cbe3" style="font-family:{SANS}">kadidiatou@data-ia : ~</text>'
    )
    desc = "Fenêtre de terminal. " + " ".join(alltext)
    write("hero.svg", svg(1200, h, "Terminal : Kadidiatou Bagayoko", desc, style, bar + "\n".join(body)))


# ---------------------------------------------------------------- carte d'identité
def idcard():
    rows = [
        ("RÔLE", "Data & AI Solutions Builder"),
        ("FORMATION", "Bachelor en Intelligence Artificielle (grade Licence), ECE Paris, 2024–2027"),
        ("RECHERCHE", "Alternance septembre 2026, 3 semaines en entreprise, 2 semaines à l'école"),
        ("EN COURS", "Partie IA du projet TCIM, portfolio avec assistant IA"),
    ]
    css = "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}@keyframes ring{from{stroke-dashoffset:300}to{stroke-dashoffset:0}}.r{animation:in .5s ease-out backwards}.ring{stroke-dasharray:300;animation:ring 1.2s ease-out .2s backwards}"
    for i in range(4):
        css += f".r{i}{{animation-delay:{0.3 + i * 0.18:.2f}s}}"
    body = [
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient></defs>',
        '<rect width="1200" height="290" rx="14" fill="url(#g)"/>',
        f'<rect width="8" height="290" fill="{GOLD}"/>',
        f'<circle cx="150" cy="120" r="48" fill="none" stroke="{GOLD}" stroke-width="4" class="ring" transform="rotate(-90 150 120)"/>',
        f'<text x="150" y="132" font-size="34" font-weight="700" fill="#ffffff" text-anchor="middle" style="font-family:{SANS}">KB</text>',
        f'<text x="150" y="212" font-size="19" font-weight="600" fill="#ffffff" text-anchor="middle" style="font-family:{SANS}">Kadidiatou</text>',
        f'<text x="150" y="236" font-size="19" font-weight="600" fill="#ffffff" text-anchor="middle" style="font-family:{SANS}">Bagayoko</text>',
        '<rect x="278" y="36" width="1" height="218" fill="#7fa3d1" opacity=".5"/>',
    ]
    for i, (k, v) in enumerate(rows):
        y = 74 + i * 56
        body.append(
            f'<g class="r r{i}"><text x="310" y="{y}" font-size="14" font-weight="700" letter-spacing="2" fill="{GOLD}" style="font-family:{SANS}">{k}</text>'
            f'<text x="310" y="{y + 26}" font-size="22" fill="#ffffff" style="font-family:{SANS}">{e(v)}</text></g>'
        )
    desc = "Carte d'identité. " + " ".join(f"{k.capitalize()} : {v}." for k, v in rows)
    write("card.svg", svg(1200, 290, "Carte d'identité", desc, css, "\n".join(body)))


# ---------------------------------------------------------------- stack à icônes
def icon_path(name):
    s = (ASSETS / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    return re.search(r'<path d="([^"]+)"', s).group(1)


def stack():
    groups = [
        ("DONNÉES", [("python", "Python"), ("pandas", "pandas"), ("plotly", "Plotly"), ("streamlit", "Streamlit"), ("jupyter", "Notebooks")]),
        ("IA", [("huggingface", "API Hugging Face"), ("claude", "Claude Code")]),
        ("OUTILS", [("hubspot", "HubSpot (compte gratuit)"), ("wordpress", "WordPress")]),
    ]
    css = "@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}.ch{animation:pop .45s ease-out backwards}"
    body = [f'<rect width="1200" height="250" rx="14" fill="{LIGHT}" stroke="{LINE}"/>']
    n = 0
    descs = []
    for gi, (g, chips) in enumerate(groups):
        y = 28 + gi * 74
        body.append(f'<text x="32" y="{y + 31}" font-size="14" font-weight="700" letter-spacing="2" fill="{NAVY}" style="font-family:{SANS}">{g}</text>')
        body.append(f'<rect x="32" y="{y + 38}" width="28" height="3" fill="{GOLD}"/>')
        x = 170
        for key, label in chips:
            w = 54 + int(len(label) * 9.6)
            css += f".h{n}{{animation-delay:{0.1 + n * 0.09:.2f}s}}"
            body.append(
                f'<g class="ch h{n}"><rect x="{x}" y="{y}" width="{w}" height="52" rx="26" fill="#ffffff" stroke="{LINE}"/>'
                f'<g transform="translate({x + 16} {y + 14}) scale(1)"><path d="{icon_path(key)}" fill="{NAVY}"/></g>'
                f'<text x="{x + 48}" y="{y + 32}" font-size="17" fill="{TEXT}" style="font-family:{SANS}">{e(label)}</text></g>'
            )
            descs.append(label)
            x += w + 14
            n += 1
    desc = "Stack. Données : Python, pandas, Plotly, Streamlit, notebooks. IA : API Hugging Face, Claude Code. Outils : HubSpot (compte gratuit), WordPress."
    write("stack.svg", svg(1200, 250, "Stack", desc, css, "\n".join(body)))


# ---------------------------------------------------------------- cartes de projets
def data_uri(path, mime, resize_w=None):
    p = ROOT / path
    if resize_w:
        im = Image.open(p).convert("RGB")
        im = im.resize((resize_w, round(im.height * resize_w / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        raw = buf.getvalue()
    else:
        raw = p.read_bytes()
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def card(fname, title, tag, thumb, bullets, stack_txt, desc):
    W, H = 600, 470
    tagw = 28 + int(len(tag) * 7.4)
    css = (
        "@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        ".b{animation:rise .5s ease-out backwards}.th{animation:rise .6s ease-out .15s backwards}.ac{transform-box:fill-box;transform-origin:0 50%;animation:grow .7s ease-out .1s backwards}"
        + "".join(f".b{i}{{animation-delay:{0.45 + i * 0.15:.2f}s}}" for i in range(3))
    )
    body = [
        f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient><clipPath id="cp"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>',
        f'<g clip-path="url(#cp)"><rect width="{W}" height="{H}" fill="{LIGHT}"/><rect width="{W}" height="58" fill="url(#g)"/></g>',
        f'<rect x="20" y="55" width="70" height="3" fill="{GOLD}" class="ac"/>',
        f'<text x="20" y="37" font-size="21" font-weight="700" fill="#ffffff" style="font-family:{SANS}">{e(title)}</text>',
        f'<rect x="{W - 20 - tagw}" y="17" width="{tagw}" height="26" rx="13" fill="{GOLD}"/>',
        f'<text x="{W - 20 - tagw / 2}" y="35" font-size="13" font-weight="700" fill="{NAVY}" text-anchor="middle" style="font-family:{SANS}">{e(tag)}</text>',
        f'<rect x="20" y="74" width="560" height="210" rx="8" fill="#ffffff" stroke="{LINE}"/>',
    ]
    if thumb:
        body.append(
            f'<image class="th" xlink:href="{thumb}" x="28" y="80" width="544" height="198" preserveAspectRatio="xMidYMid meet"/>'
        )
    for i, b in enumerate(bullets):
        y = 316 + i * 32
        body.append(
            f'<g class="b b{i}"><rect x="22" y="{y - 10}" width="8" height="8" fill="{GOLD}"/>'
            f'<text x="42" y="{y}" font-size="16.5" fill="{TEXT}" style="font-family:{SANS}">{e(b)}</text></g>'
        )
    body.append(f'<rect x="20" y="416" width="560" height="1" fill="{LINE}"/>')
    body.append(
        f'<text x="20" y="444" font-size="14" fill="{NAVY}" style="font-family:{SANS}"><tspan font-weight="700" letter-spacing="1.5">STACK</tspan><tspan dx="12">{e(stack_txt)}</tspan></text>'
    )
    write(fname, svg(W, H, title, desc, css, "\n".join(body)))


def cards():
    shot = data_uri("assets/screens/dashboard-1.png", "image/png", 1100)
    wm = data_uri("assets/charts/wmdp_danger_by_category.svg", "image/svg+xml")
    rv = data_uri("assets/charts/revops_field_normalization.svg", "image/svg+xml")
    card(
        "card-dashboard.svg", "Dashboard e-commerce", "Janvier 2026", shot,
        ["397 884 lignes de transactions (18 532 factures)", "CA de £8,91M, panier moyen de £481", "6 indicateurs et 6 graphiques, Royaume-Uni à 82 %"],
        "Python, pandas, Streamlit, Plotly",
        "Dashboard e-commerce, janvier 2026. 397 884 lignes de transactions (18 532 factures). CA de £8,91M, panier moyen de £481. 6 indicateurs et 6 graphiques, Royaume-Uni à 82 %. Python, pandas, Streamlit, Plotly. Vignette : capture du dashboard.",
    )
    card(
        "card-wmdp.svg", "Hackathon WMDP", "Mars 2026, autrice unique", wm,
        ["250 prompts adversariaux, 5 types de reformulation", "6 LLMs, 360 requêtes, 234 réponses non vides", "0 % de refus sur Llama et Qwen (mots-clés)"],
        "API Hugging Face",
        "Hackathon WMDP, mars 2026, autrice unique. 250 prompts adversariaux en 5 types de reformulation. 6 LLMs open source, 360 requêtes, 234 réponses non vides. 0 % de refus sur Llama et Qwen, mesuré par mots-clés. API Hugging Face. Vignette : graphique de dangerosité par catégorie.",
    )
    card(
        "card-revops.svg", "Audit migration CRM", "Données synthétiques", rv,
        ["734 comptes et 5 234 contacts (Kaggle)", "Contract_Status : 8 valeurs brutes, 3 après normalisation", "Audit avant migration Salesforce vers HubSpot"],
        "pandas, matplotlib, notebook",
        "Audit de qualité de données avant migration Salesforce vers HubSpot, sur données synthétiques Kaggle. 734 comptes et 5 234 contacts. Contract_Status : 8 valeurs brutes, 3 après normalisation. pandas, matplotlib, notebook. Vignette : graphique de normalisation par champ.",
    )


# ---------------------------------------------------------------- en construction
def building():
    W, H = 600, 470
    css = (
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}@keyframes slide{from{transform:translateX(0)}to{transform:translateX(400px)}}"
        ".dot{animation:pulse 1.6s ease-in-out infinite}.sg{transform:translateX(200px);animation:slide 2.4s ease-in-out infinite alternate}"
    )
    items = [
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
    body = [
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient><clipPath id="tr"><rect width="520" height="6" rx="3"/></clipPath></defs>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>',
        f'<rect width="8" height="{H}" fill="{GOLD}"/>',
        f'<circle class="dot" cx="38" cy="36" r="6" fill="{GOLD}"/>',
        f'<text x="54" y="42" font-size="21" font-weight="700" fill="#ffffff" style="font-family:{SANS}">En construction</text>',
    ]
    y = 84
    for name, tag, lines in items:
        body.append(f'<text x="30" y="{y}" font-size="18" font-weight="700" fill="#ffffff" style="font-family:{SANS}">{e(name)}</text>')
        body.append(f'<text x="570" y="{y}" font-size="13" font-weight="700" fill="{GOLD}" text-anchor="end" style="font-family:{SANS}">{e(tag)}</text>')
        body.append(
            f'<g transform="translate(30 {y + 12})"><rect width="520" height="6" rx="3" fill="#ffffff" opacity=".18"/>'
            f'<g clip-path="url(#tr)"><rect class="sg" width="120" height="6" rx="3" fill="{GOLD}"/></g></g>'
        )
        ly = y + 46
        for ln in lines:
            body.append(f'<rect x="30" y="{ly - 9}" width="7" height="7" fill="{GOLD}"/><text x="46" y="{ly}" font-size="15" fill="#e6edf5" style="font-family:{SANS}">{e(ln)}</text>')
            ly += 26
        y = ly + 26
    desc = "En construction. " + " ".join(f"{n} ({t}) : " + ". ".join(ls) + "." for n, t, ls in items)
    write("building.svg", svg(W, H, "En construction", desc, css, "\n".join(body)))


# ---------------------------------------------------------------- schéma besoin -> solution
def flow():
    nodes = [
        (18, "1", "Données", ["397 884 lignes de transactions", "(e-commerce)", "", "5 234 contacts (RevOps)"]),
        (320, "2", "Nettoyage", ["Fiabilisation des données", "(Consulat du Mali)", "", "Audit qualité avant migration", "(RevOps)"]),
        (622, "3", "Modèle ou analyse", ["TF-IDF + Random Forest", "(TCIM)", "", "Analyse des processus", "(Consulat du Mali)", "", "LLMs via l'API Hugging Face", "(WMDP)"]),
        (924, "4", "Dashboard", ["Streamlit + Plotly", "", "KPIs et reporting pour la", "direction"]),
    ]
    loop = "M62 292H1138A24 24 0 0 1 1162 316A24 24 0 0 1 1138 340H62A24 24 0 0 1 38 316A24 24 0 0 1 62 292Z"
    dur = 10
    css = (
        f".nd{{animation:lit {dur}s linear infinite}}"
        f"@keyframes lit{{0%{{fill:#fff;stroke:{NAVY}}}2%,12%{{fill:#fbf2de;stroke:{GOLD}}}16%,100%{{fill:#fff;stroke:{NAVY}}}}}"
        ".p{opacity:0}"
        "@media (prefers-reduced-motion: reduce){.p{display:none}}"
    )
    delays = [0.2, 1.5, 2.8, 4.1]
    body = [f'<rect width="1200" height="364" rx="14" fill="{LIGHT}"/>']
    body.append(f'<path d="{loop}" fill="none" stroke="{NAVY2}" stroke-width="2" stroke-dasharray="6 6" opacity=".55"/>')
    for i, (x, num, title, lines) in enumerate(nodes):
        cx = x + 129
        body.append(f'<line x1="{cx}" y1="264" x2="{cx}" y2="292" stroke="{NAVY2}" stroke-width="2"/><circle cx="{cx}" cy="292" r="5" fill="{NAVY2}"/>')
        body.append(f'<rect class="nd" style="animation-delay:{delays[i]}s" x="{x}" y="24" width="258" height="240" rx="12" fill="#ffffff" stroke="{NAVY}" stroke-width="2"/>')
        body.append(
            f'<circle cx="{x + 34}" cy="58" r="16" fill="{GOLD}"/><text x="{x + 34}" y="64" font-size="18" font-weight="700" fill="{NAVY}" text-anchor="middle" style="font-family:{SANS}">{num}</text>'
            f'<text x="{x + 58}" y="64" font-size="18" font-weight="700" fill="{NAVY}" style="font-family:{SANS}">{e(title)}</text>'
            f'<rect x="{x + 20}" y="84" width="40" height="3" fill="{GOLD}"/>'
        )
        ly = 114
        for ln in lines:
            if ln:
                body.append(f'<text x="{x + 20}" y="{ly}" font-size="14" fill="{TEXT}" style="font-family:{SANS}">{e(ln)}</text>')
            ly += 17 if ln else 8
    n = 7
    for k in range(n):
        b = f"-{k * dur / n:.2f}s"
        body.append(
            f'<g class="p"><circle r="5.5" fill="{GOLD}" stroke="{NAVY}" stroke-width="1.5"/>'
            f'<set attributeName="opacity" to="1" begin="0s"/>'
            f'<animateMotion dur="{dur}s" begin="{b}" repeatCount="indefinite" path="{loop}"/></g>'
        )
    desc = (
        "Schéma en quatre étapes, avec des particules qui circulent entre elles. 1, Données : 397 884 lignes de transactions (e-commerce), 5 234 contacts (RevOps). "
        "2, Nettoyage : fiabilisation des données (Consulat du Mali), audit qualité avant migration (RevOps). "
        "3, Modèle ou analyse : TF-IDF + Random Forest (TCIM), analyse des processus (Consulat du Mali), LLMs via l'API Hugging Face (WMDP). "
        "4, Dashboard : Streamlit + Plotly, KPIs et reporting pour la direction."
    )
    write("flow.svg", svg(1200, 364, "Du besoin à la solution", desc, css, "\n".join(body)))


if __name__ == "__main__":
    hero()
    idcard()
    stack()
    cards()
    building()
    flow()
