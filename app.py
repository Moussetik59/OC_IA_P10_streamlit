# Import des librairies nécessaires
import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import io

# Import du client Azure Blob Storage
from azure.storage.blob import BlobServiceClient

# Définition des constantes
CONTAINER_NAME = "models"

# Lecture des variables d'environnement nécessaires pour accéder au Storage Account
storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
storage_account_key = os.getenv("AZURE_STORAGE_KEY")

# Initialisation du client Azure Blob Storage en utilisant la clé du compte
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=storage_account_key
)

# Fonction pour télécharger le fichier clicks_sample.csv depuis le Blob Storage et le convertir en DataFrame
def load_clicks_csv():
    """Télécharge clicks_sample.csv depuis le conteneur 'models' et retourne un DataFrame."""
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob="clicks_sample.csv"
    )
    data = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))
    return df

# Chargement des variables d'environnement depuis un fichier .env local (utile pour le mode local)
if os.path.exists(".env"):
    load_dotenv()
    st.sidebar.success("Fichier .env chargé avec succès")
else:
    st.sidebar.warning("Fichier .env non trouvé, utilisant les valeurs par défaut.")

# Détection du mode d'exécution : local ou déployé sur Azure
USE_AZURE = os.getenv("USE_AZURE", "False").lower() == "true"
API_URL = os.getenv("AZURE_FUNCTION_URL")

# Affichage dans la sidebar pour information
if USE_AZURE:
    if API_URL:
        st.sidebar.info("Mode : Déploiement Azure")
    else:
        st.sidebar.error("Erreur : AZURE_FUNCTION_URL non défini.")
else:
    # En mode local, j'utilise une URL d'API Flask locale
    API_URL = "http://127.0.0.1:5000/api/recommend_articles"
    st.sidebar.warning("Mode : Local (Flask API)")

# Fonction pour charger dynamiquement la liste des utilisateurs à partir du CSV
# La fonction est mise en cache pour éviter des téléchargements répétés inutiles
@st.cache_data
def load_users():
    try:
        clicks_df = load_clicks_csv()
        user_ids = clicks_df["user_id"].unique().tolist()
        return sorted(user_ids)
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSV depuis Azure Blob : {e}")
        return []

# Début de l'interface utilisateur Streamlit
st.title("Système de Recommandation d'Articles")

# Chargement et affichage de la liste des utilisateurs dans un menu déroulant
user_ids = load_users()
if user_ids:
    user_id = st.selectbox("Sélectionnez votre ID utilisateur :", user_ids)
else:
    st.error("Impossible de charger la liste des utilisateurs.")

# Lorsqu'on clique sur le bouton, la requête est envoyée à l'API pour obtenir les recommandations
if st.button("Obtenir des recommandations"):
    if not API_URL:
        st.error("API non configurée. Vérifiez AZURE_FUNCTION_URL.")
    else:
        # Construction de l'URL de requête avec l'ID utilisateur en paramètre
        if '?' in API_URL:
            url = f"{API_URL}&user_id={user_id}"
        else:
            url = f"{API_URL}?user_id={user_id}"

        # Affichage d'un spinner pendant la récupération des recommandations
        with st.spinner("Recherche des meilleurs articles..."):
            try:
                # Requête HTTP GET vers l'API
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                recommendations = response.json()

                # Affichage des recommandations obtenues
                if not recommendations:
                    st.warning("Aucune recommandation disponible pour cet utilisateur.")
                else:
                    st.subheader("Articles recommandés :")
                    for idx, article in enumerate(recommendations, start=1):
                        st.write(f"Article {idx}: {article}")

            except requests.exceptions.Timeout:
                st.error("Erreur : Délai d’attente dépassé pour l'API.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur dans la récupération des recommandations : {e}")
