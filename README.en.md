<p align="right"><a href="README.md">Version française</a></p>

<p align="center">
  <img src="assets/hero.svg" alt="Banner (text in French). Kadidiatou Bagayoko. Student in Artificial Intelligence &amp; Data Science. Villiers-sur-Marne, France; kadibaga22@gmail.com; LinkedIn. Passionate about data and AI, looking for a work-study placement (alternance) in Data &amp; AI from October 2026. Quote: understand the need, build the solution, deliver the impact." width="100%">
</p>

<p align="center">
  <img src="assets/chips/dispo.svg" alt="Disponibilité octobre 2026 (available from October 2026)">
  <img src="assets/chips/alternance.svg" alt="Alternance 2026-2027 · à partir d'octobre (work-study 2026-2027, from October)">
  <img src="assets/chips/major.svg" alt="Major de promo B2 2025-2026 · ECE Paris (top of the class, second year 2025-2026, ECE Paris)">
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

> The visuals and the availability chips are in French; the text below is translated.

## ◆ About

I design and build Data & AI solutions.

- **Role**: Data & AI Solutions Builder
- **Education**: Bachelor 3 in Data & Artificial Intelligence, ECE Paris
- **Open to**: work-study placement 2026-2027, 3 weeks at the company / 2 weeks at school
- **I build**: dashboards, custom systems, automation, machine learning, AI assistants

I don't stop at analysis: I build complete solutions, from the business need to deployment.

Portfolio: link coming soon

<p align="center">
  <img src="assets/flow.svg" alt="Diagram (text in French): from need to solution, through innovative digital strategies. Four steps linked by a gold thread, checked off one after another. 1, Need: process analysis and recommendations presented to the Consul (Consulate of Mali). 2, Cleaning: 397,884 transaction rows cleaned (e-commerce), quality audit of 5,234 contacts (RevOps). 3, Model / analysis: TF-IDF + Random Forest (TCIM), LLMs through the Hugging Face API (WMDP). 4, Dashboard: Streamlit + Plotly, KPIs and reporting for management." width="100%">
</p>

## ◆ Experience

| Year | Organisation | Role | What I did |
|---|---|---|---|
| 2026, since April | TCIM / Skills4Mind | AI part (ongoing) | Automatic classification of health data (TF-IDF + Random Forest), 82.5% accuracy. Project presentation on request. |
| 2026, April to June | Consulate of Mali | Data & Digital Innovation intern | At the Consulate of Mali, I analysed processes, made data more reliable and presented optimisation recommendations to the Consul, which led to a 50% reduction in users' trips. *(estimate)* |
| 2025, June to September | Femmes Audacieuses | Data analysis & Business | KPIs and reporting for management: +30% engagement. |

## ◆ Projects

<p align="center">
  <img src="assets/projet-tcim.svg" alt="Featured project (text in French), since April 2026: TCIM, securing health data. Areas: Machine Learning, Data Engineering, Automation, Dashboard. The need: automatically detect sensitive medical data, without human intervention. What I built: a TF-IDF + Random Forest model (scikit-learn) trained on about 190 annotated medical texts, within a 3-layer decision: rules, model, arbiter; data classified as sensitive is encrypted automatically. The result: detection without human intervention, a compliance score out of 100 recalculated in real time and an automated PDF report. Figures: 82.5% precision, 300 trees, project graded 19.75/20." width="100%">
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/13N5upENpWyv9IF96Au_A_JO1EgVglR6O/view?usp=sharing"><img src="assets/chips/demo-video-en.svg" alt="Watch the video demo"></a>
</p>

<details>
<summary><b>TCIM, securing health data</b>: 82.5% precision, project graded 19.75/20</summary>

**Context**: since April 2026, AI part of the TCIM / Skills4Mind project. The goal is to automatically spot sensitive medical data, on synthetic data generated with Faker (50 patients, 66 accounts).

**Method**: supervised scikit-learn model (TF-IDF + Random Forest with 300 trees) trained on about 190 annotated medical texts, within a 3-layer decision: deterministic rules, ML model, arbiter. Recall favoured by design: in a sensitive context, a missed record costs more than a false positive. Random Forest chosen for its explainability and the size of the corpus.

**Value**: automatic encryption of data classified as sensitive (Fernet, AES-128 CBC + HMAC-SHA256), intrusion detection on 4 attack vectors with alerts and account blocking, automated PDF report. Compliance score out of 100 (encryption 30%, traceability 30%, access control 20%, completeness 20%) recalculated in real time by SQL aggregation queries on PostgreSQL (after a migration from SQLite), and tracked in a Chart.js dashboard (KPIs, sensitivity breakdown, access by role).

[Watch the video demo](https://drive.google.com/file/d/13N5upENpWyv9IF96Au_A_JO1EgVglR6O/view?usp=sharing) · Project presentation on request

</details>

<details>
<summary><b>E-commerce dashboard</b>: 397,884 transaction rows, 6 indicators and 6 charts</summary>

**Context**: January 2026. Analyse the activity of an e-commerce site from 397,884 transaction rows (18,532 invoices).

**Method**: cleaning and analysis with Python and pandas, then a Streamlit + Plotly dashboard with 6 indicators and 6 charts.

**Value**: a quick read of the activity: revenue of £8.91M on cleaned data, average basket of £481, United Kingdom at 82% of revenue.

[GitHub repository](https://github.com/Kadi2207/ecommerce-dashboard-analytics) · see the screenshots below

</details>

<details>
<summary><b>WMDP hackathon</b>: 6 open-source LLMs evaluated, 0% refusals on Llama and Qwen</summary>

**Context**: March 2026, sole author. Evaluate the safety of open-source LLMs against adversarial prompts.

**Method**: corpus of 250 adversarial prompts in 5 rephrasing types (direct, academic, contextual, role, fragmented); 6 LLMs queried through the Hugging Face API on 60 prompts, i.e. 360 requests.

**Value**: 0% refusals on Llama and Qwen (4 models), measured by keyword detection. Documented limit: the empty answers of the DeepSeek-R1 models skew their score, so no valid comparison is made about them.

[GitHub repository](https://github.com/Kadi2207/wmdp-cyber)

</details>

<details>
<summary><b>CRM migration audit (RevOps)</b>: quality of 734 accounts and 5,234 contacts before migration</summary>

**Context**: prepare a Salesforce to HubSpot migration, on synthetic data from Kaggle (no company data).

**Method**: data quality audit of 734 accounts and 5,234 contacts in a pandas / matplotlib notebook.

**Value**: spot quality issues before the migration rather than after the import. In addition, on a free HubSpot account: import of 950 contacts with mapping and 0 errors.

[GitHub repository](https://github.com/Kadi2207/revops-crm-migration-analysis)

</details>

## ◆ The dashboard in pictures

Real screenshots of the e-commerce dashboard (Streamlit + Plotly), cropped to the charts.

<p align="center">
  <img src="assets/capture-dashboard-1.svg" alt="Dashboard screenshot: monthly revenue line and bars of the top 10 countries by revenue, led by the United Kingdom." width="100%">
</p>

*Monthly revenue (December 2011 partial) and top 10 countries: the United Kingdom accounts for 82% of revenue.*

<p align="center">
  <img src="assets/capture-dashboard-2.svg" alt="Dashboard screenshot: bars of the top 10 products by quantity sold and bars of revenue by day of the week." width="100%">
</p>

*Top 10 products by quantity sold and revenue by day of the week.*

<p align="center">
  <img src="assets/capture-dashboard-3.svg" alt="Dashboard screenshot: line of revenue by hour of the day and histogram of transaction amounts." width="100%">
</p>

*Revenue by hour of the day and distribution of transaction amounts.*

## ◆ Stack

**Data**<br>
<img src="assets/chips/stack-python.svg" alt="Python"> <img src="assets/chips/stack-sql.svg" alt="SQL"> <img src="assets/chips/stack-pandas.svg" alt="pandas"> <img src="assets/chips/stack-matplotlib.svg" alt="matplotlib"> <img src="assets/chips/stack-plotly.svg" alt="Plotly"> <img src="assets/chips/stack-streamlit.svg" alt="Streamlit">

**AI / ML**<br>
<img src="assets/chips/stack-tf-idf-random-forest.svg" alt="TF-IDF + Random Forest"> <img src="assets/chips/stack-api-hugging-face.svg" alt="Hugging Face API">

**Dev**<br>
<img src="assets/chips/stack-notebooks.svg" alt="Notebooks"> <img src="assets/chips/stack-claude-code.svg" alt="Claude Code"> <img src="assets/chips/stack-wordpress.svg" alt="WordPress">

**Tools**<br>
<img src="assets/chips/stack-hubspot-compte-gratuit.svg" alt="HubSpot (free account)"> <img src="assets/chips/stack-aws-cloud-foundations.svg" alt="AWS (Cloud Foundations)">

## ◆ Activity

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake-dark.svg">
    <img src="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake.svg" alt="Decorative animation: a gold snake moves across the GitHub contribution graph, from midnight blue to gold." width="100%">
  </picture>
</p>

## ◆ Contact

<p align="center">
  <img src="assets/contact.svg" alt="Contact panel (text in French): let's build something useful. Open to opportunities in Data, Machine Learning and AI. Available. LinkedIn: linkedin.com/in/kadi-bagayoko. Email: kadibaga22@gmail.com. GitHub: github.com/Kadi2207." width="100%">
</p>

<p align="center">
  <a href="https://linkedin.com/in/kadi-bagayoko">LinkedIn</a> · <a href="mailto:kadibaga22@gmail.com">kadibaga22@gmail.com</a> · <a href="https://github.com/Kadi2207">GitHub</a> · Portfolio: link coming soon
</p>

<p align="center">
  <img src="assets/footer.svg" alt="Decorative strip: beige wave, gold line, midnight-blue line and diamonds." width="100%">
</p>
