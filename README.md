# MyContent - Interface de Recommandation d'Articles

Cette application permet de visualiser les recommandations d'articles pour les utilisateurs du service **MyContent**.

L'interface est développée en **Streamlit** et se connecte à une **API Azure Functions** pour récupérer les recommandations.

---

## Fonctionnement

- La liste des utilisateurs est extraite du fichier `clicks_sample.csv` stocké dans **Azure Blob Storage**.
- Les recommandations sont pré-calculées et stockées dans un fichier `precomputed_recos.csv` lu directement par l'API.
- Le Streamlit envoie une requête vers l'API en fonction de l'ID utilisateur sélectionné.

---

## Architecture

Utilisateur → Interface Streamlit → Appel API Azure Function → Lecture precomputed_recos.csv → Réponse API → Affichage

---

## Lancement local

1️⃣ Installer les dépendances :

```bash
pip install -r requirements.txt
```

2️⃣ Lancer l'application :

```bash
streamlit run app.py
```