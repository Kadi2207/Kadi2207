<p align="right"><a href="README.en.md">English version</a></p>

<p align="center">
  <img src="assets/hero.svg" alt="Kadidiatou Bagayoko. Étudiante en Intelligence Artificielle &amp; Data Science. Villiers-sur-Marne, France ; kadibaga22@gmail.com ; LinkedIn. Passionnée par la data et l'IA, je recherche une alternance en Data &amp; IA à partir d'octobre 2026. Citation : Comprendre le besoin, construire la solution, livrer l'impact." width="100%">
</p>

<p align="center">
  <img src="assets/chips/dispo.svg" alt="Disponibilité octobre 2026">
  <img src="assets/chips/alternance.svg" alt="Alternance 2026-2027 · à partir d'octobre">
  <img src="assets/chips/major.svg" alt="Major de promo B2 2025-2026 · ECE Paris">
</p>

<p align="center">
  <img src="assets/chips/ml.svg" alt="Machine Learning">
  <img src="assets/chips/genai.svg" alt="GenAI">
  <img src="assets/chips/python.svg" alt="Python">
  <img src="assets/chips/sql.svg" alt="SQL">
  <img src="assets/chips/data-analysis.svg" alt="Data Analysis">
</p>

<p align="center">
  <a href="https://linkedin.com/in/kadi-bagayoko">LinkedIn</a> · <a href="mailto:kadibaga22@gmail.com">kadibaga22@gmail.com</a>
</p>

## ◆ À propos

Je développe et conçois des solutions Data & IA.

- **Rôle** : Data & AI Solutions Builder
- **Formation** : Bachelor 3 Data & Intelligence Artificielle, ECE Paris
- **Ouverte pour** : Alternance 2026-2027, 3 sem. entreprise / 2 sem. école
- **Je construis** : dashboards, systèmes sur mesure, automatisation, machine learning, assistants IA

Je ne m'arrête pas à l'analyse : je construis des solutions complètes, du besoin métier jusqu'au déploiement.

Portfolio : lien à venir

<p align="center">
  <img src="assets/flow.svg" alt="Du besoin à la solution, à travers des stratégies digitales innovantes. Quatre étapes reliées par un fil d'or, validées l'une après l'autre. 1, Besoin : analyse des processus et recommandations présentées au Consul (Consulat du Mali). 2, Nettoyage : 397 884 lignes de transactions nettoyées (e-commerce), audit qualité de 5 234 contacts (RevOps). 3, Modèle / analyse : TF-IDF + Random Forest (TCIM), LLMs via l'API Hugging Face (WMDP). 4, Dashboard : Streamlit + Plotly, KPIs et reporting pour la direction." width="100%">
</p>

## ◆ Expériences

| Année | Structure | Rôle | Ce que j'ai fait |
|---|---|---|---|
| 2026, depuis avril | TCIM / Skills4Mind | Partie IA (en cours) | Classification automatique de données de santé (TF-IDF + Random Forest), accuracy de 82,5 %. Présentation du projet sur demande. |
| 2026, avril à juin | Consulat du Mali | Stagiaire Data & Innovation Digitale | Au Consulat du Mali, j'ai analysé les processus, fiabilisé les données et présenté des recommandations d'optimisation au Consul, avec à la clé une réduction de 50 % des déplacements des usagers. *(estimation)* |
| 2025, juin à septembre | Femmes Audacieuses | Analyse de données & Business | KPIs et reporting pour la direction : +30 % d'engagement. |

## ◆ Projets

<p align="center">
  <img src="assets/projet-tcim.svg" alt="Projet en vedette, depuis avril 2026 : TCIM, sécurisation de données de santé. Volets : Machine Learning, Data Engineering, Automatisation, Dashboard. Le besoin : détecter automatiquement les données médicales sensibles, sans intervention humaine. Ce que j'ai construit : un modèle TF-IDF + Random Forest (scikit-learn) entraîné sur environ 190 textes médicaux annotés, dans une décision à 3 couches : règles, modèle, arbitre ; les données classées sensibles sont chiffrées automatiquement. Le résultat : une détection sans intervention humaine, un score de conformité sur 100 recalculé en temps réel et un rapport PDF automatisé. Chiffres : 82,5 % de précision, 300 arbres, projet noté 19,75/20." width="100%">
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/13N5upENpWyv9IF96Au_A_JO1EgVglR6O/view?usp=sharing"><img src="assets/chips/demo-video.svg" alt="Voir la démo vidéo"></a>
</p>

<details>
<summary><b>TCIM, sécurisation de données de santé</b> : 82,5 % de précision, projet noté 19,75/20</summary>

**Contexte** : depuis avril 2026, partie IA du projet TCIM / Skills4Mind. Il s'agit de repérer automatiquement les données médicales sensibles, sur des données synthétiques générées avec Faker (50 patients, 66 comptes).

**Méthode** : modèle supervisé scikit-learn (TF-IDF + Random Forest de 300 arbres) entraîné sur environ 190 textes médicaux annotés, dans une décision à 3 couches : règles déterministes, modèle ML, arbitre. Rappel privilégié par choix : dans un contexte sensible, une donnée manquée coûte plus cher qu'un faux positif. Random Forest choisi pour son explicabilité et la taille du corpus.

**Valeur** : chiffrement automatique des données classées sensibles (Fernet, AES-128 CBC + HMAC-SHA256), détection d'intrusion sur 4 vecteurs d'attaque avec alertes et blocage de comptes, rapport PDF automatisé. Score de conformité sur 100 (chiffrement 30 %, traçabilité 30 %, contrôle d'accès 20 %, complétude 20 %) recalculé en temps réel par requêtes SQL d'agrégation sur PostgreSQL (après migration depuis SQLite), et suivi dans un dashboard Chart.js (KPI, répartition de la sensibilité, accès par rôle).

[Voir la démo vidéo](https://drive.google.com/file/d/13N5upENpWyv9IF96Au_A_JO1EgVglR6O/view?usp=sharing) · Présentation du projet sur demande

</details>

<details>
<summary><b>Dashboard e-commerce</b> : 397 884 lignes de transactions, 6 indicateurs et 6 graphiques</summary>

**Contexte** : janvier 2026. Analyser l'activité d'un site e-commerce à partir de 397 884 lignes de transactions (18 532 factures).

**Méthode** : nettoyage et analyse avec Python et pandas, puis restitution dans un dashboard Streamlit + Plotly de 6 indicateurs et 6 graphiques.

**Valeur** : une lecture rapide de l'activité : chiffre d'affaires de £8,91 M sur données nettoyées, panier moyen de £481, Royaume-Uni à 82 % du chiffre d'affaires.

[Dépôt GitHub](https://github.com/Kadi2207/ecommerce-dashboard-analytics) · voir les captures ci-dessous

</details>

<details>
<summary><b>Hackathon WMDP</b> : 6 LLMs open source évalués, 0 % de refus sur Llama et Qwen</summary>

**Contexte** : mars 2026, autrice unique. Évaluer la sécurité de LLMs open source face à des prompts adversariaux.

**Méthode** : corpus de 250 prompts adversariaux en 5 types de reformulation (direct, académique, contextuel, rôle, fragmenté) ; 6 LLMs interrogés via l'API Hugging Face sur 60 prompts, soit 360 requêtes.

**Valeur** : 0 % de refus sur Llama et Qwen (4 modèles), mesuré par détection de mots-clés. Limite documentée : les réponses vides des modèles DeepSeek-R1 faussent leur score, aucune comparaison valide n'est faite à leur sujet.

[Dépôt GitHub](https://github.com/Kadi2207/wmdp-cyber)

</details>

<details>
<summary><b>Audit migration CRM (RevOps)</b> : qualité de 734 comptes et 5 234 contacts avant migration</summary>

**Contexte** : préparer une migration Salesforce vers HubSpot, sur données synthétiques issues de Kaggle (aucune donnée d'entreprise).

**Méthode** : audit de qualité des données de 734 comptes et 5 234 contacts dans un notebook pandas / matplotlib.

**Valeur** : repérer les problèmes de qualité avant la migration plutôt qu'après l'import. En complément, sur un compte HubSpot gratuit : import de 950 contacts avec mapping et 0 erreur.

[Dépôt GitHub](https://github.com/Kadi2207/revops-crm-migration-analysis)

</details>

## ◆ Le dashboard en images

Captures réelles du dashboard e-commerce (Streamlit + Plotly), recadrées sur les graphiques.

<p align="center">
  <img src="assets/capture-dashboard-1.svg" alt="Capture du dashboard : courbe du chiffre d'affaires mensuel et barres du top 10 des pays par chiffre d'affaires, dominé par le Royaume-Uni." width="100%">
</p>

*Chiffre d'affaires mensuel (décembre 2011 partiel) et top 10 des pays : le Royaume-Uni pèse 82 % du chiffre d'affaires.*

<p align="center">
  <img src="assets/capture-dashboard-2.svg" alt="Capture du dashboard : barres du top 10 des produits par quantité vendue et barres du chiffre d'affaires par jour de la semaine." width="100%">
</p>

*Top 10 des produits par quantité vendue et chiffre d'affaires par jour de la semaine.*

<p align="center">
  <img src="assets/capture-dashboard-3.svg" alt="Capture du dashboard : courbe du chiffre d'affaires par heure de la journée et histogramme du montant des transactions." width="100%">
</p>

*Chiffre d'affaires par heure de la journée et distribution du montant des transactions.*

## ◆ Stack

**Data**<br>
<img src="assets/chips/stack-python.svg" alt="Python"> <img src="assets/chips/stack-sql.svg" alt="SQL"> <img src="assets/chips/stack-pandas.svg" alt="pandas"> <img src="assets/chips/stack-matplotlib.svg" alt="matplotlib"> <img src="assets/chips/stack-plotly.svg" alt="Plotly"> <img src="assets/chips/stack-streamlit.svg" alt="Streamlit">

**IA / ML**<br>
<img src="assets/chips/stack-tf-idf-random-forest.svg" alt="TF-IDF + Random Forest"> <img src="assets/chips/stack-api-hugging-face.svg" alt="API Hugging Face">

**Dév**<br>
<img src="assets/chips/stack-notebooks.svg" alt="Notebooks"> <img src="assets/chips/stack-claude-code.svg" alt="Claude Code"> <img src="assets/chips/stack-wordpress.svg" alt="WordPress">

**Outils**<br>
<img src="assets/chips/stack-hubspot-compte-gratuit.svg" alt="HubSpot (compte gratuit)"> <img src="assets/chips/stack-aws-cloud-foundations.svg" alt="AWS (Cloud Foundations)">

## ◆ Activité

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake-dark.svg">
    <img src="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake.svg" alt="Animation décorative : un serpent doré parcourt le graphe de contributions GitHub, du bleu nuit au doré." width="100%">
  </picture>
</p>

## ◆ Contact

<p align="center">
  <img src="assets/contact.svg" alt="Construisons quelque chose d'utile. Ouverte aux opportunités en Data, Machine Learning et IA. Disponible. LinkedIn : linkedin.com/in/kadi-bagayoko. Email : kadibaga22@gmail.com. GitHub : github.com/Kadi2207." width="100%">
</p>

<p align="center">
  <a href="https://linkedin.com/in/kadi-bagayoko">LinkedIn</a> · <a href="mailto:kadibaga22@gmail.com">kadibaga22@gmail.com</a> · <a href="https://github.com/Kadi2207">GitHub</a> · Portfolio : lien à venir
</p>

<p align="center">
  <img src="assets/footer.svg" alt="Bandeau décoratif : vague beige, filet doré, filet bleu nuit et losanges." width="100%">
</p>
