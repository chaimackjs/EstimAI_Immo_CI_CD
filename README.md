# EstimAI Immo CI/CD

Ce dépôt contient les trois workflows du projet EstimAI Immo : qualité du
code, intégration continue et réentraînement hebdomadaire.

Le déploiement est accepté uniquement si le R² du prix total sur le jeu de
test est strictement supérieur à 0,70. Après l'entraînement, la CI recharge le
modèle, vérifie sa version et exécute des prédictions positives et finies.

Les artefacts publiés contiennent le modèle, les métriques, les importances de
variables, les erreurs par type, le rapport de qualité des données, le
manifeste des sources et la version du modèle. Cette version contient le numéro
de workflow, le SHA Git, la date UTC et l'empreinte SHA-256 du manifeste.

Le workflow de qualité exécute les tests avec une couverture minimale de 70 %,
vérifie la documentation et audite les dépendances avec `pip-audit`. Après une
mise à jour du modèle, la CI contrôle aussi que
<https://estimaiimmo.streamlit.app/> est publiquement accessible. En cas
d'échec sur la branche principale, une issue GitHub est créée ou actualisée.

Le secret GitHub Actions `APP_REPO_TOKEN` doit contenir un jeton ayant le droit
`contents: write` sur `chaimackjs/EstimAI_Immo`. Sans ce secret, un workflow
exécuté depuis un autre dépôt ne peut pas pousser le nouveau modèle.
