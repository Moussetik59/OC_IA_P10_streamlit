```markdown
# OC_IA_P10_STREAMLIT_APP

Ce dépôt contient l’application Streamlit permettant d’interagir avec le système de recommandation d’articles. L’objectif est de fournir une **interface utilisateur** intuitive pour sélectionner un utilisateur et obtenir instantanément des recommandations.

---

## Fonctionnalités

- **Sélection d’un ID utilisateur** depuis un menu déroulant.  
- **Bouton “Obtenir des recommandations”** pour faire un appel API à l’Azure Function (hébergée dans [OC_IA_P10_RecoFunction](https://github.com/preudh/OC_IA_P10_RecoFunction)).  
- **Affichage** de la liste d’articles recommandés.  
- **Gestion** d’un mode “local” ou “Azure” (selon la valeur de certaines variables d’environnement), pour pointer vers l’API appropriée.

---

## Démo en ligne

L’application est déployée et accessible à l’adresse :  
[https://p10-streamlit-app-2025.azurewebsites.net/](https://p10-streamlit-app-2025.azurewebsites.net/)

---

## Installation et exécution (localement)

1. **Cloner le dépôt** :  
   ```bash
   git clone https://github.com/preudh/OC_IA_P10_STREAMLIT_APP.git
   ```
2. **Installer les dépendances** (dans un environnement virtuel recommandé) :  
   ```bash
   pip install -r requirements.txt
   ```
3. **Créer et configurer le fichier `.env`** (optionnel, selon votre besoin) pour définir :  
   - `USE_AZURE` = `True` ou `False`  
   - `AZURE_FUNCTION_URL` = URL de la fonction Azure (ex. `https://<nom-fonction>.azurewebsites.net/api/recommend_articles?...`)  
   - `AZURE_STORAGE_ACCOUNT` = nom du compte de stockage Azure (si nécessaire)
4. **Exécuter l’application Streamlit** :  
   ```bash
   streamlit run app.py
   ```
   Rendez-vous ensuite sur [http://localhost:8501](http://localhost:8501) pour accéder à l’interface.

---

## Déploiement et recommandations

- **Pour un déploiement Azure** :  
  - Il est préférable d’utiliser **Visual Studio Code** et son extension **Azure Tools**, ce qui facilite grandement l’authentification, la configuration et le déploiement de l’application Streamlit vers un service d’hébergement (Azure Web App ou autre).
  - Vous pouvez configurer un pipeline CI/CD (avec GitHub Actions ou Azure DevOps) pour automatiser le déploiement sur Azure.

- **Stockage des données** :  
  - L’application Streamlit peut (au besoin) se connecter à **Azure Blob Storage** pour récupérer des fichiers (ex. le CSV des clics). Le code fait usage de `BlobServiceClient` et de `azure.identity`.  
  - Assurez-vous de bien configurer les variables d’environnement (`AZURE_STORAGE_ACCOUNT`, `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`, etc.) pour l’authentification.

---

## Architecture globale

Cette application Streamlit n’est qu’un composant d’une **architecture serverless** plus vaste :

- **[OC_IA_P10_RecoFunction](https://github.com/preudh/OC_IA_P10_RecoFunction)** : Héberge l’API de recommandation avec Azure Functions.  
- **[OC_IA_P10_Recommandation_contenu](https://github.com/preudh/OC_IA_P10_Recommandation_contenu)** : Contient le Notebook pour entraîner et tester le modèle ALS (filtrage collaboratif).

Le **frontend** Streamlit envoie une requête `GET` vers l’API Azure Function pour obtenir les recommandations, puis les affiche à l’utilisateur.

