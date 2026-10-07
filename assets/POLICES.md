# Polices des visuels

Les SVG du profil et les graphiques ne chargent aucune police : le texte est converti en tracés par `scripts/build_svgs.py` (fontTools) et `scripts/make_charts.py` (matplotlib). Les fichiers de police ne sont pas dans le dépôt.

| Police | Usage | Autrice ou auteur | Licence | Source |
|---|---|---|---|---|
| Playfair Display | Nom, titres, chiffres clés | Claus Eggers Sørensen | SIL Open Font License 1.1 | paquet npm `@fontsource/playfair-display` 5.3.0 |
| Source Sans 3 | Texte courant, libellés, graphiques | Paul D. Hunt (Adobe) | SIL Open Font License 1.1 | paquet npm `@fontsource/source-sans-3` 5.3.0 |

Récupération, dans un dossier vide : `npm pack @fontsource/playfair-display --ignore-scripts` et `npm pack @fontsource/source-sans-3 --ignore-scripts`, puis `tar -xzf` de chaque `.tgz`. Regrouper les `.woff` des deux dossiers `package/files` dans un même dossier, passé aux scripts avec `--fonts`.

Logos de la stack : voir `assets/icons/SOURCES.md`.
