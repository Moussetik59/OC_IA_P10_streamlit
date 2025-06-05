import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

import io
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "models"
storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT")

# Crée un client vers le compte de stockage en s'authentifiant via DefaultAzureCredential
credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=credential
)

def load_clicks_csv():
    """Télécharge clicks_sample.csv depuis le conteneur "models" puis retourne un DataFrame."""
    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob="clicks_sample.csv"
    )
    data = blob_client.download_blob().readall()
    df = pd.read_csv(io.BytesIO(data))
    return df

# ✅ Charger les variables d'environnement
if os.path.exists(".env"):
    load_dotenv()
    st.sidebar.success("✅ Fichier .env chargé avec succès")
else:
    st.sidebar.warning("⚠️ Fichier .env non trouvé, utilisant les valeurs par défaut.")

# ✅ Définir l'URL de l'API en fonction du mode
USE_AZURE = os.getenv("USE_AZURE", "False").lower() == "true"
API_URL = os.getenv("AZURE_FUNCTION_URL")

if USE_AZURE:
    if API_URL:
        st.sidebar.info("🌍 Mode : **Déploiement Azure**")
    else:
        st.sidebar.error("❌ Erreur : AZURE_FUNCTION_URL non défini...")
else:
    # Mode local (on a pas de '?code=...')
    API_URL = "http://127.0.0.1:5000/api/recommend_articles"
    st.sidebar.warning("🖥️ Mode : **Local (Flask API)**")

# ✅ Charger la liste des utilisateurs depuis Azure Blob Storage
@st.cache_data
def load_users():
    try:
        clicks_df = load_clicks_csv()
        user_ids = clicks_df["user_id"].unique().tolist()
        return sorted(user_ids)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du CSV depuis Azure Blob : {e}")
        return []

# ✅ Interface utilisateur Streamlit
st.title("🔍 Système de Recommandation d'Articles")

# Sélection dynamique de l'utilisateur
user_ids = load_users()
if user_ids:
    user_id = st.selectbox("👤 Sélectionnez votre ID utilisateur :", user_ids)
else:
    st.error("❌ Impossible de charger la liste des utilisateurs.")

# ✅ Lancer la recommandation si un ID est sélectionné
if st.button("🎯 Obtenir des recommandations"):
    if not API_URL:
        st.error("❌ API non configurée. Vérifiez `AZURE_FUNCTION_URL` dans `.env` ou les variables d'Azure.")
    else:
        # Gestion automatique du point d'interrogation :
        # - Si API_URL contient déjà '?code=...' -> on ajoute '&'
        # - Sinon -> on ajoute '?'
        if '?' in API_URL:
            url = f"{API_URL}&user_id={user_id}"
        else:
            url = f"{API_URL}?user_id={user_id}"

        with st.spinner("🔍 Recherche des meilleurs articles..."):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                recommendations = response.json()

                if not recommendations:
                    st.warning("⚠️ Aucune recommandation disponible pour cet utilisateur.")
                else:
                    st.subheader("📌 Articles recommandés :")
                    for idx, article in enumerate(recommendations, start=1):
                        st.write(f"📖 **Article {idx}**: {article}")

            except requests.exceptions.Timeout:
                st.error("❌ Erreur : Délai d’attente dépassé pour l’API.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Erreur dans la récupération des recommandations : {e}")

