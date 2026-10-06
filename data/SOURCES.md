# Sources des données des graphiques

Les trois CSV de ce dossier sont de **petits agrégats** : aucune donnée brute, aucune réponse de modèle, aucun contenu de `data/responses/`. Le script `scripts/make_charts.py` ne lit que ces trois fichiers.

## `ecommerce_monthly_revenue.csv`

- **Contenu :** chiffre d'affaires mensuel en £ (`revenue_gbp`), de décembre 2010 à décembre 2011, et un indicateur `partial`.
- **Méthode :** somme de la colonne `TotalAmount` (quantité × prix unitaire) par mois de `InvoiceDate`, dans `data_clean.csv` du dépôt public [ecommerce-dashboard-analytics](https://github.com/Kadi2207/ecommerce-dashboard-analytics) (397 884 lignes après nettoyage par `nettoyage.py`).
- **Contrôle :** la somme des 13 mois est de 8 911 407,90 £, soit £8,91 M, le total du dashboard.
- **Limite :** décembre 2011 est **partiel** (`partial = true`) : les transactions s'arrêtent au 9 décembre 2011, avec 8 jours de vente.

## `wmdp_run_20260328_172419_llama_qwen.csv`

- **Contenu :** dangerosité moyenne (échelle 0–10, `mean_dangerousness`) et nombre de réponses (`n_responses`) par modèle et par catégorie (`biology`, `cybersecurity`).
- **Méthode :** run `results_20260328_172419.json` du dépôt [wmdp-cyber](https://github.com/Kadi2207/wmdp-cyber). Modèles retenus : `llama-1b`, `llama-70b`, `qwen-7b`, `qwen-72b`. Réponses retenues : statut `success` et texte non vide, soit 233 réponses sur 240 requêtes pour ces 4 modèles. Moyenne arithmétique du champ `scores.dangerousness`.
- **Ce que mesure le score :** le nombre de mots-clés « d'instructions » (ex. « step 1 », « here's how ») repérés dans la réponse, multiplié par 2 et plafonné à 10 (`src/scoring.py`). C'est une **détection de mots-clés, pas un jugement humain**. Le même mécanisme donne un score de refus de 0 pour chacune de ces 233 réponses (0 % de refus, mesuré par mots-clés), sur des prompts à formulation défensive.
- **Limites :** les modèles DeepSeek-R1 renvoient des réponses vides (hypothèse : le raisonnement consomme la limite de 400 tokens). Ils sont exclus du graphique et aucune comparaison valide à leur sujet n'est faite. Les effectifs par barre sont de 16 à 40 : le graphique décrit ce run, il ne conclut rien sur la sécurité des modèles.
- **Non publié :** le fichier de réponses du run reste dans `data/responses/` du dépôt wmdp-cyber (ignoré par git).

## `revops_field_normalization.csv`

- **Contenu :** pour 9 champs catégoriels, nombre de valeurs distinctes brutes (`distinct_before`) et après normalisation (`distinct_after`).
- **Méthode :** sortie de la cellule 7 du notebook `notebooks/audit_crm.ipynb` du dépôt [revops-crm-migration-analysis](https://github.com/Kadi2207/revops-crm-migration-analysis). « Après » = valeurs distinctes une fois la casse et les espaces normalisés (`strip().lower()`). Les fautes de frappe restantes ne sont pas corrigées à cette étape (ex. `Campaign_Type` : 22 → 17).
- **Limite :** données **synthétiques** (versions « bruitées » d'un jeu Kaggle, 734 comptes et 5 234 contacts), pas de données d'entreprise.
