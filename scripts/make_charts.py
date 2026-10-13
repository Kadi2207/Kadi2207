"""Génère les 2 graphiques dessinés du profil (WMDP, RevOps) en SVG, à partir de petits CSV d'agrégats.

Lit uniquement data/wmdp_run_20260328_172419_llama_qwen.csv et data/revops_field_normalization.csv
(jamais data/responses/ ni des données brutes). Le dashboard e-commerce est montré par ses captures réelles
(assets/capture-dashboard-*.svg, scripts/build_svgs.py) : aucun graphique n'est régénéré pour lui.
Sortie : assets/charts/*.svg (texte converti en tracés : rendu identique partout).

Style : fond bleu nuit propre au SVG (coins arrondis, rendu identique sur GitHub clair et sombre),
texte clair, barres dorées. Source et limites de chaque graphique : légende du README et data/SOURCES.md.

Usage, depuis la racine du dépôt :
    pip install pandas matplotlib fonttools
    python scripts/make_charts.py --fonts <dossier des .woff>

Polices (SIL Open Font License 1.1, voir assets/POLICES.md) : Playfair Display pour les titres, Source Sans 3
pour le reste, mêmes fichiers .woff que scripts/build_svgs.py, convertis en .ttf dans un dossier temporaire.
Sans --fonts, matplotlib utilise DejaVu Sans.
"""
import argparse
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Patch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "assets" / "charts"

# Charte bleu nuit (passe finale)
NAVY, TEXT, MUTED, GOLD = "#0f2038", "#e8eef5", "#b7c3d3", "#C9953B"
SKY = "#7f97bd"  # second série : bleu clair, distinct du doré en luminance et en teinte
GRID = "#2a3d5c"
TITLE_FONT = {}

plt.rcParams.update({
    "svg.fonttype": "path",          # texte -> tracés
    "svg.hashsalt": "kadi2207",      # identifiants stables d'une exécution à l'autre
    "font.family": ["DejaVu Sans"],
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": TEXT,
})


def load_fonts(folder):
    """Convertit les .woff en .ttf (temporaires) et les déclare à matplotlib."""
    from fontTools.ttLib import TTFont
    from matplotlib import font_manager

    tmp = Path(tempfile.mkdtemp())
    for name in ("source-sans-3-latin-400-normal", "source-sans-3-latin-600-normal", "source-sans-3-latin-700-normal", "playfair-display-latin-700-normal"):
        f = TTFont(str(Path(folder) / f"{name}.woff"))
        f.flavor = None
        f.save(str(tmp / f"{name}.ttf"))
        font_manager.fontManager.addfont(str(tmp / f"{name}.ttf"))
    plt.rcParams["font.family"] = ["Source Sans 3", "DejaVu Sans"]  # DejaVu pour les flèches absentes de Source Sans
    TITLE_FONT.update(family=["Playfair Display", "DejaVu Sans"])


def fr(x, nd=2):
    """Nombre au format français (virgule décimale)."""
    return f"{x:.{nd}f}".replace(".", ",")


def card(width, height, title, subtitle):
    """Figure : carte bleu nuit à coins arrondis (transparente autour), titre clair, filet doré."""
    fig = plt.figure(figsize=(width, height))
    fig.patch.set_alpha(0)
    fig.patches.append(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.025", transform=fig.transFigure,
                                      facecolor=NAVY, edgecolor=GOLD, linewidth=1, alpha=1, mutation_aspect=width / height, zorder=-10))
    fig.add_artist(plt.Line2D([0.05, 0.12], [0.93, 0.93], color=GOLD, lw=3, transform=fig.transFigure))
    fig.text(0.05, 0.89, title, fontsize=19, fontweight="bold", color=TEXT, va="top", **TITLE_FONT)
    fig.text(0.05, 0.80, subtitle, fontsize=13.5, color=MUTED, va="top")
    return fig


def style(ax):
    ax.patch.set_alpha(0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, format="svg", transparent=True, metadata={"Date": None})  # pas d'horodatage : sorties reproductibles
    plt.close(fig)
    print(f"ok assets/charts/{name}")


def chart_wmdp():
    d = pd.read_csv(DATA / "wmdp_run_20260328_172419_llama_qwen.csv")
    names = {"llama-1b": "Llama-1B", "llama-70b": "Llama-70B", "qwen-7b": "Qwen-7B", "qwen-72b": "Qwen-72B"}
    cats = [("biology", "Biologie", SKY), ("cybersecurity", "Cybersécurité", GOLD)]

    fig = card(8, 5.2, "WMDP : dangerosité moyenne par catégorie",
               "Score par mots-clés de 0 à 10, Llama et Qwen, run du 28 mars 2026")
    ax = fig.add_axes([0.1, 0.13, 0.86, 0.52])
    style(ax)
    models = list(names)
    w = 0.36
    for k, (cat, label, color) in enumerate(cats):
        xs, vs = [], []
        for i, m in enumerate(models):
            row = d[(d.model == m) & (d.category == cat)].iloc[0]
            xs.append(i + (k - 0.5) * w)
            vs.append(row.mean_dangerousness)
        ax.bar(xs, vs, width=w * 0.9, color=color, label=label)
        for x, v in zip(xs, vs):
            ax.text(x, v + 0.04, fr(v), ha="center", va="bottom", fontsize=12.5, color=TEXT)
    ax.set_xticks(range(len(models)), [names[m] for m in models], fontsize=14)
    ax.set_ylim(0, 10)
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.tick_params(axis="y", labelsize=12.5)
    ax.yaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in cats], frameon=False, fontsize=13.5, loc="upper right",
              ncol=2, labelcolor=TEXT)
    save(fig, "wmdp_danger_by_category.svg")


def chart_revops():
    d = pd.read_csv(DATA / "revops_field_normalization.csv")
    fig = card(8, 7.4, "Audit CRM : valeurs distinctes par champ",
               "Avant et après normalisation de la casse et des espaces, données synthétiques")
    ax = fig.add_axes([0.33, 0.06, 0.62, 0.66])
    style(ax)
    n = len(d)
    h = 0.38
    for i, r in d.iterrows():
        y = n - 1 - i
        ax.barh(y + h / 2, r.distinct_before, height=h * 0.9, color=SKY)
        ax.barh(y - h / 2, r.distinct_after, height=h * 0.9, color=GOLD)
        ax.text(r.distinct_before + 0.3, y + h / 2, str(r.distinct_before), va="center", fontsize=12, color=MUTED)
        ax.text(r.distinct_after + 0.3, y - h / 2, str(r.distinct_after), va="center", fontsize=12, color=TEXT, fontweight="bold")
    ax.set_yticks(range(n), [f"{r.field}" for r in d.iloc[::-1].itertuples()], fontsize=12.5)
    ax.set_xlim(0, d.distinct_before.max() + 3)
    ax.set_xticks([])
    ax.legend(handles=[Patch(color=SKY, label="Valeurs brutes"), Patch(color=GOLD, label="Après normalisation")],
              frameon=False, fontsize=13.5, loc="lower right", ncol=1, labelcolor=TEXT)
    # séparation Companies / Employees
    split = n - d[d.dataset == "Companies"].shape[0] - 0.5
    ax.axhline(split, color=GRID, lw=1, ls="--")
    ax.text(ax.get_xlim()[1], n - 0.5, "Companies", ha="right", va="bottom", fontsize=12, color=MUTED)
    ax.text(ax.get_xlim()[1], split - 0.08, "Employees", ha="right", va="top", fontsize=12, color=MUTED)
    save(fig, "revops_field_normalization.svg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", help="dossier des .woff de @fontsource/playfair-display et @fontsource/source-sans-3")
    a = ap.parse_args()
    if a.fonts:
        load_fonts(a.fonts)
    chart_wmdp()
    chart_revops()
