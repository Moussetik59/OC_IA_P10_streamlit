# Import des librairies nécessaires
import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import io
from azure.storage.blob import BlobServiceClient

# Constantes
CONTAINER_NAME = "models"
BLOB_NAME = "clicks_sample.csv"

# Chargement des variables d'environnement
if os.path.exists(".env"):
    load_dotenv()

# Lecture des variables d'environnement pour accéder au Storage Account
storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
storage_account_key = os.getenv("AZURE_STORAGE_KEY")
api_url = os.getenv("AZURE_FUNCTION_URL")

# Initialisation du client Azure Blob Storage
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=storage_account_key
)

# Fonction pour charger le fichier clicks_sample.csv
@st.cache_data
def load_users():
    """
    Charge le fichier clicks_sample.csv depuis Azure Blob Storage
    et retourne la liste triée des user_id disponibles.
    """
    try:
        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=BLOB_NAME
        )
        data = blob_client.download_blob().readall()
        df = pd.read_csv(io.BytesIO(data))
        user_ids = df["user_id"].unique().tolist()
        return sorted(user_ids)
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSV : {e}")
        return []

# Début de l'interface utilisateur Streamlit
st.title("Système de Recommandation d'Articles")

# Introduction
st.markdown(
    """
    Cette application vous permet d'obtenir des recommandations personnalisées
    d'articles en fonction de votre historique de lecture.

    Sélectionnez un ID utilisateur dans la liste ci-dessous pour voir les articles
    les plus pertinents pour vous.
    """
)

# Chargement et affichage de la liste des utilisateurs
user_ids = load_users()
if user_ids:
    user_id = st.selectbox("ID utilisateur :", user_ids)
else:
    st.error("Impossible de charger la liste des utilisateurs.")
    st.stop()

# Bouton pour obtenir les recommandations
if st.button("Obtenir des recommandations"):
    if not api_url:
        st.error("L'URL de l'API n'est pas configurée (AZURE_FUNCTION_URL).")
    else:
        # Construction de l'URL de requête
        if '?' in api_url:
            url = f"{api_url}&user_id={user_id}"
        else:
            url = f"{api_url}?user_id={user_id}"

        # Appel à l'API
        with st.spinner("Chargement des recommandations..."):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                recommendations = response.json()

                # Affichage des résultats
                if not recommendations:
                    st.warning("Aucune recommandation disponible pour cet utilisateur.")
                else:
                    st.subheader(f"Articles recommandés pour l'utilisateur {user_id} :")
                    st.markdown("_Du plus pertinent au moins pertinent._")

                    # Affichage stylisé
                    for idx, article in enumerate(recommendations, start=1):
                        st.write(f"**{idx}. Article ID : {article}**")

            except requests.exceptions.Timeout:
                st.error("Erreur : Délai d’attente dépassé pour l'API.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur lors de l'appel à l'API : {e}")
