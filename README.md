# MyContent - Interface de Recommandation d'Articles

Cette interface permet aux utilisateurs de **MyContent** de visualiser leurs recommandations d'articles.

Elle est développée avec **Streamlit** et consomme l'API REST déployée sur Azure.

---

## Fonctionnement

- L'utilisateur saisit un `user_id` dans l'interface.
- Streamlit envoie une requête à l'API Azure Function.
- L'API consulte le fichier `precomputed_recos.csv` sur Blob Storage et renvoie les recommandations.
- Streamlit affiche les 5 articles recommandés.

---

## Architecture de l'application

```text
Utilisateur → Interface Streamlit → Appel API Azure Function → Lecture precomputed_recos.csv → Réponse → Affichage des recommandations
```

---

## Remarque

- La liste des `user_id` autorisés provient désormais de `precomputed_recos.csv` (full dataset).
- L'interface est conçue pour démontrer un fonctionnement complet en conditions réelles (MVP).