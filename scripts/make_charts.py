"""Génère les 3 graphiques du profil (SVG) à partir de petits CSV d'agrégats.

Lit uniquement les 3 fichiers de data/ (jamais data/responses/ ni des données brutes).
Sortie : assets/charts/*.svg (texte converti en tracés : rendu identique partout).

Usage, depuis la racine du dépôt :
    pip install pandas matplotlib
    python scripts/make_charts.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "assets" / "charts"

NAVY, BLUE, GOLD = "#1e3a5f", "#2c5282", "#c8901a"
SKY, BG, TEXT, MUTED = "#9db4d3", "#f5f8fc", "#2c3e50", "#52647b"

plt.rcParams.update({
    "svg.fonttype": "path",          # texte -> tracés
    "svg.hashsalt": "kadi2207",      # identifiants stables d'une exécution à l'autre
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#c5d2e3",
    "axes.labelcolor": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
    "text.color": TEXT,
})

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def fr(x, nd=2):
    """Nombre au format français (virgule décimale)."""
    return f"{x:.{nd}f}".replace(".", ",")


def card(width, height, title, subtitle, footnote):
    """Figure-carte : fond #f5f8fc, titre bleu nuit, filet or, note de bas de page."""
    fig = plt.figure(figsize=(width, height), facecolor=BG)
    fig.add_artist(plt.Line2D([0.045, 0.105], [0.945, 0.945], color=GOLD, lw=3, transform=fig.transFigure))
    fig.text(0.045, 0.905, title, fontsize=15, fontweight="bold", color=NAVY, va="top")
    fig.text(0.045, 0.845, subtitle, fontsize=10.5, color=MUTED, va="top")
    fig.text(0.045, 0.035, footnote, fontsize=8.6, color=MUTED, va="bottom", linespacing=1.5)
    return fig


def style(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, format="svg", facecolor=BG, metadata={"Date": None})  # pas d horodatage : sorties reproductibles
    plt.close(fig)
    print(f"ok assets/charts/{name}")


def chart_ecommerce():
    d = pd.read_csv(DATA / "ecommerce_monthly_revenue.csv")
    d["partial"] = d["partial"].astype(str).str.lower().eq("true")
    labels = []
    for i, m in enumerate(d["month"]):
        y, mo = int(m[:4]), int(m[5:])
        lab = MOIS[mo - 1]
        labels.append(f"{lab}\n{y}" if i == 0 or mo == 1 else lab)

    fig = card(10, 5.4, "Chiffre d'affaires mensuel, déc. 2010 → déc. 2011",
               "Dashboard e-commerce · somme de TotalAmount par mois, en millions de £",
               "Source : data_clean.csv du dépôt ecommerce-dashboard-analytics (397 884 lignes, total £"
               f"{fr(d['revenue_gbp'].sum() / 1e6)} M).\nLimite : décembre 2011 est partiel (données jusqu'au 9 décembre, 8 jours de vente).")
    ax = fig.add_axes([0.09, 0.2, 0.88, 0.5])
    style(ax)
    vals = d["revenue_gbp"] / 1e6
    peak = vals.idxmax()
    for i, (v, p) in enumerate(zip(vals, d["partial"])):
        if p:
            ax.bar(i, v, color="#dfe8f4", edgecolor=BLUE, hatch="////", linewidth=1.2, width=0.68)
        else:
            ax.bar(i, v, color=GOLD if i == peak else BLUE, width=0.68)
    ax.text(peak, vals[peak] + 0.025, f"£{fr(vals[peak])} M", ha="center", va="bottom", fontsize=10, fontweight="bold", color=NAVY)
    last = len(d) - 1
    ax.text(last, vals[last] + 0.025, f"£{fr(vals[last])} M\n(partiel)", ha="center", va="bottom", fontsize=9, color=NAVY)
    ax.set_xticks(range(len(d)), labels, fontsize=9)
    ax.set_ylim(0, 1.35)
    ax.set_yticks([0, 0.4, 0.8, 1.2], [fr(t, 1) for t in (0, 0.4, 0.8, 1.2)], fontsize=9)
    ax.yaxis.grid(True, color="#dbe5f1", lw=0.8)
    ax.set_axisbelow(True)
    save(fig, "ecommerce_monthly_revenue.svg")


def chart_wmdp():
    d = pd.read_csv(DATA / "wmdp_run_20260328_172419_llama_qwen.csv")
    names = {"llama-1b": "Llama-1B", "llama-70b": "Llama-70B", "qwen-7b": "Qwen-7B", "qwen-72b": "Qwen-72B"}
    cats = [("biology", "Biologie", SKY), ("cybersecurity", "Cybersécurité", NAVY)]
    n_total = int(d["n_responses"].sum())

    fig = card(10, 5.4, "WMDP : dangerosité moyenne par catégorie",
               "Score par mots-clés de 0 à 10, Llama et Qwen (4 modèles), run du 28 mars 2026",
               f"Source : run 20260328_172419, {n_total} réponses non vides sur 240 requêtes (modèles DeepSeek exclus).\n"
               "Limites : mesure par détection de mots-clés, pas un jugement humain ; 0 % de refus sur ces modèles (mots-clés),\n"
               "prompts à formulation défensive. Aucune conclusion de sécurité n'en est tirée.")
    ax = fig.add_axes([0.09, 0.27, 0.88, 0.43])
    style(ax)
    models = list(names)
    w = 0.34
    for k, (cat, label, color) in enumerate(cats):
        xs, vs = [], []
        for i, m in enumerate(models):
            row = d[(d.model == m) & (d.category == cat)].iloc[0]
            xs.append(i + (k - 0.5) * w)
            vs.append(row.mean_dangerousness)
        ax.bar(xs, vs, width=w * 0.92, color=color, label=label)
        for x, v in zip(xs, vs):
            ax.text(x, v + 0.12, fr(v), ha="center", va="bottom", fontsize=9, color=NAVY)
    ax.set_xticks(range(len(models)), [names[m] for m in models], fontsize=10)
    ax.set_ylim(0, 10)
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.tick_params(axis="y", labelsize=9)
    ax.yaxis.grid(True, color="#dbe5f1", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_ylabel("Dangerosité (0–10)", fontsize=9)
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in cats], frameon=False, fontsize=9.5, loc="upper right", ncol=2)
    save(fig, "wmdp_danger_by_category.svg")


def chart_revops():
    d = pd.read_csv(DATA / "revops_field_normalization.csv")
    fig = card(10, 6.4, "RevOps : valeurs distinctes avant / après normalisation",
               "9 champs catégoriels de l'audit CRM · normalisation de la casse et des espaces",
               "Données synthétiques (versions « bruitées » d'un jeu Kaggle) : 734 comptes, 5 234 contacts, aucune donnée d'entreprise.\n"
               "Source : cellule 7 du notebook audit_crm.ipynb. « Après » = casse et espaces normalisés ; les fautes de frappe restantes\n"
               "(ex. Campaign_Type : 22 → 17) ne sont pas corrigées à cette étape.")
    ax = fig.add_axes([0.27, 0.2, 0.69, 0.52])
    style(ax)
    n = len(d)
    h = 0.36
    for i, r in d.iterrows():
        y = n - 1 - i
        ax.barh(y + h / 2, r.distinct_before, height=h * 0.92, color=SKY)
        ax.barh(y - h / 2, r.distinct_after, height=h * 0.92, color=NAVY)
        ax.text(r.distinct_before + 0.3, y + h / 2, str(r.distinct_before), va="center", fontsize=9, color=TEXT)
        ax.text(r.distinct_after + 0.3, y - h / 2, str(r.distinct_after), va="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_yticks(range(n), [f"{r.field}" for r in d.iloc[::-1].itertuples()], fontsize=9)
    ax.set_xlim(0, d.distinct_before.max() + 3)
    ax.xaxis.grid(True, color="#dbe5f1", lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_xlabel("Nombre de valeurs distinctes", fontsize=9)
    # séparation Companies / Employees
    split = n - d[d.dataset == "Companies"].shape[0] - 0.5
    ax.axhline(split, color="#c5d2e3", lw=1, ls="--")
    ax.text(ax.get_xlim()[1], n - 0.55, "Companies", ha="right", va="bottom", fontsize=8.5, color=MUTED)
    ax.text(ax.get_xlim()[1], split - 0.05, "Employees", ha="right", va="top", fontsize=8.5, color=MUTED)
    ax.legend(handles=[Patch(color=SKY, label="Valeurs brutes"), Patch(color=NAVY, label="Après normalisation")],
              frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.35, 1.13), ncol=2)
    save(fig, "revops_field_normalization.svg")


if __name__ == "__main__":
    chart_ecommerce()
    chart_wmdp()
    chart_revops()
