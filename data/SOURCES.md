# Sources des données

Le CSV de ce dossier est un **petit agrégat** : aucune donnée brute. Aucun graphique du profil n'est généré à partir de lui ; le dashboard e-commerce est montré par ses captures réelles. Il reste ici comme contrôle du total de £8,91 M.

## `ecommerce_monthly_revenue.csv`

- **Contenu :** chiffre d'affaires mensuel en £ (`revenue_gbp`), de décembre 2010 à décembre 2011, et un indicateur `partial`.
- **Méthode :** somme de la colonne `TotalAmount` (quantité × prix unitaire) par mois de `InvoiceDate`, dans `data_clean.csv` du dépôt public [ecommerce-dashboard-analytics](https://github.com/Kadi2207/ecommerce-dashboard-analytics) (397 884 lignes après nettoyage par `nettoyage.py`).
- **Contrôle :** la somme des 13 mois est de 8 911 407,90 £, soit £8,91 M, le total du dashboard.
- **Limite :** décembre 2011 est **partiel** (`partial = true`) : les transactions s'arrêtent au 9 décembre 2011, avec 8 jours de vente.
