<p align="right"><a href="README.md">Version française</a></p>

<p align="center">
  <img src="assets/hero.svg" alt="Banner (text in French). Kadidiatou Bagayoko. Data analysis, dashboard building, machine learning. Using data &amp; AI to design innovative solutions." width="100%">
</p>

<p align="center">
  <img src="assets/disponibilite.svg" alt="Availability strip (text in French): available for a work-study placement (alternance) from October 2026. Data analysis, data science, AI." width="100%">
</p>

<p align="center">
  <a href="https://linkedin.com/in/kadi-bagayoko"><img src="https://img.shields.io/badge/LinkedIn-kadi--bagayoko-C9953B?style=flat-square&labelColor=0f2038" alt="LinkedIn: linkedin.com/in/kadi-bagayoko"></a>
  <a href="mailto:kadibaga22@gmail.com"><img src="https://img.shields.io/badge/Email-kadibaga22%40gmail.com-C9953B?style=flat-square&labelColor=0f2038" alt="Email: kadibaga22@gmail.com"></a>
</p>

> The visuals are in French; the captions below are translated.

## ◆ About

Student specialising in data and artificial intelligence.

At the Consulate of Mali, I analysed processes, made data more reliable and presented optimisation recommendations to the Consul, which led to a 50% reduction in users' trips.

Portfolio: link coming soon

## ◆ Experience

<details>
<summary><b>Consulate of Mali</b> · Data &amp; Digital Innovation intern · April to June 2026</summary>

- Process analysis.
- Data reliability work.
- Optimisation recommendations presented to the Consul.
- Result: 50% reduction in users' trips.

</details>

<details>
<summary><b>Femmes Audacieuses</b> · Data analysis &amp; Business · June to September 2025</summary>

- KPIs and reporting for management.
- Result: +30% engagement.

</details>

## ◆ From need to solution

<p align="center">
  <img src="assets/flow.svg" alt="Four-step diagram linked by a gold thread. 1, Data: 397,884 transaction rows (e-commerce), 5,234 contacts (RevOps). 2, Cleaning: data reliability (Consulate of Mali), quality audit before migration (RevOps). 3, Model or analysis: TF-IDF + Random Forest (TCIM), process analysis (Consulate of Mali), LLMs through the Hugging Face API (WMDP). 4, Dashboard: Streamlit + Plotly, KPIs and reporting for management." width="100%">
</p>

## ◆ Projects

<p align="center">
  <a href="https://github.com/Kadi2207/ecommerce-dashboard-analytics"><img src="assets/card-dashboard.svg" alt="E-commerce dashboard, January 2026. Cleaning and analysis of 397,884 transaction rows with pandas. Presented in a Streamlit dashboard with 6 indicators and 6 charts, on revenue of £8.91M. Python, pandas, Streamlit, Plotly. Link to the repository." width="100%"></a>
</p>

<p align="center">
  <a href="https://github.com/Kadi2207/wmdp-cyber"><img src="assets/card-wmdp.svg" alt="WMDP hackathon, March 2026, sole author. Design of a corpus of 250 adversarial prompts in 5 rephrasing types. Evaluation of 6 open-source LLMs through the Hugging Face API, over 360 requests: 0% refusal on Llama and Qwen, measured by keyword detection. Link to the repository." width="100%"></a>
</p>

<p align="center">
  <a href="https://github.com/Kadi2207/revops-crm-migration-analysis"><img src="assets/card-revops.svg" alt="CRM migration audit, synthetic data. Data quality audit of 734 accounts and 5,234 contacts ahead of a Salesforce to HubSpot migration. Work on synthetic data from Kaggle: no company data. pandas, matplotlib, notebook. Link to the repository." width="100%"></a>
</p>

<p align="center">
  <img src="assets/building.svg" alt="Under construction: TCIM / Skills4Mind (since April 2026, AI part, automatic classification of health data, 82.5% accuracy, project presentation on request) and a portfolio with an AI chatbot assistant (link coming soon)." width="100%">
</p>

Repositories: [e-commerce dashboard](https://github.com/Kadi2207/ecommerce-dashboard-analytics) · [WMDP](https://github.com/Kadi2207/wmdp-cyber) · [CRM audit](https://github.com/Kadi2207/revops-crm-migration-analysis). TCIM has no public repository: project presentation on request.

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

## ◆ Charts

Two charts produced by [scripts/make_charts.py](scripts/make_charts.py) (pandas + matplotlib) from small aggregate CSV files; the method for each one is in [data/SOURCES.md](data/SOURCES.md).

<p align="center">
  <img src="assets/charts/wmdp_danger_by_category.svg" alt="Average dangerousness on a 0 to 10 scale, by category, for Llama-1B, Llama-70B, Qwen-7B and Qwen-72B: between 0 and 0.10 in biology, between 0.65 and 1.00 in cybersecurity." width="100%">
</p>

*WMDP hackathon, run of 28 March 2026: average dangerousness (0 to 10) of the responses from Llama-1B, Llama-70B, Qwen-7B and Qwen-72B, i.e. 233 non-empty responses out of 240 requests. Limitations: the score is keyword detection, not a human judgement; the 0% refusal is also measured by keywords, on prompts with a defensive wording. No safety conclusion is drawn from it, and the DeepSeek-R1 models (empty responses) are not in this chart.*

<p align="center">
  <img src="assets/charts/revops_field_normalization.svg" alt="Horizontal bars of the number of distinct values before and after case normalisation for 9 fields, for example Contract_Status from 8 to 3 and Seniority_Level from 12 to 5." width="100%">
</p>

*CRM audit: number of distinct values per categorical field before and after normalising case and whitespace (cell 7 of the notebook). Limitation: synthetic data (“noisy” versions of a Kaggle dataset), no company data; the remaining typos are not corrected at this step.*

## ◆ Stack

<p align="center">
  <img src="assets/stack.svg" alt="Stack. Data: Python, pandas, matplotlib, Plotly, Streamlit. AI / ML: TF-IDF + Random Forest, Hugging Face API. Dev: notebooks, Claude Code, WordPress. Tools: HubSpot (free account), AWS (Cloud Foundations)." width="100%">
</p>

## ◆ Education and certifications

- Bachelor in Artificial Intelligence (Licence level), Data & AI specialisation, ECE Paris, 2024-2027
- AWS Academy Graduate, Cloud Foundations (Amazon Web Services, 2025)
- Structuring Data & Exploring GenAI Tools (OMNES Education, 2025)
- Prompt Engineering Fundamentals (Datascientest, 2024)

## ◆ Public speaking and team projects

Interview at VivaTech (Orbite Média) · asked by OMNES Education for an interview on AI · 1st place in a team robotics project.

## ◆ Activity

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake-dark.svg">
    <img src="https://raw.githubusercontent.com/Kadi2207/Kadi2207/output/github-snake.svg" alt="Decorative animation: a gold snake moves across the GitHub contribution graph, from midnight blue to gold." width="100%">
  </picture>
</p>

## ◆ Contact

I am looking for a work-study placement in Data & AI starting October 2026, with 3 weeks at the company and 2 weeks at school.

[LinkedIn](https://linkedin.com/in/kadi-bagayoko) · [kadibaga22@gmail.com](mailto:kadibaga22@gmail.com) · Portfolio: link coming soon

<p align="center">
  <img src="assets/footer.svg" alt="Decorative strip: midnight-blue wave, gold line and diamonds." width="100%">
</p>
