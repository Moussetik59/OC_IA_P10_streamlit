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
BLOB_NAME = "precomputed_recos.csv"

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
    Charge le fichier precomputed_recos.csv depuis Azure Blob Storage
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

# --- Ajout du logo ---
st.image("logo.png", width=300)

# --- Titre de la page ---
st.title("Système de Recommandation d'Articles")

# --- Introduction ---
st.markdown(
    """
    Cette application permet de visualiser les recommandations d'articles
    générées par le moteur de recommandation **MyContent**.

    Vous pouvez sélectionner un utilisateur ci-dessous pour obtenir les
    **5 articles les plus recommandés** pour lui, parmi l'ensemble des articles disponibles.
    """
)

# --- Chargement de la liste des utilisateurs ---
user_ids = load_users()
min_user_id = min(user_ids) if user_ids else 0
max_user_id = max(user_ids) if user_ids else 0

# --- Saisie manuelle de l'utilisateur ---
st.markdown("**Veuillez saisir un ID utilisateur compris entre** `{}` **et** `{}` :".format(min_user_id, max_user_id))

user_id_input = st.number_input(
    "ID utilisateur", 
    min_value=min_user_id, 
    max_value=max_user_id, 
    step=1
)

# --- Validation : vérifier que l'ID existe ---
if user_id_input in user_ids:
    user_id_valid = True
    user_id = int(user_id_input)
else:
    user_id_valid = False

# --- Bouton pour obtenir les recommandations ---
if st.button("Obtenir des recommandations"):
    if not user_id_valid:
        st.error(f"Erreur : l'ID utilisateur {int(user_id_input)} n'existe pas dans les données.")
    elif not api_url:
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

                # --- Affichage des résultats ---
                if not recommendations:
                    st.warning("Aucune recommandation disponible pour cet utilisateur.")
                else:
                    st.subheader(f"Top 5 des articles recommandés pour l'utilisateur {user_id} :")
                    st.markdown("_Articles classés par niveau de recommandation._")

                    # Icônes pour les 3 premiers
                    medals = ["🥇", "🥈", "🥉"]

                    # Affichage stylisé
                    for idx, article in enumerate(recommendations, start=1):
                        if idx <= 3:
                            st.write(f"{medals[idx-1]} **Article ID : {article}**")
                        else:
                            st.write(f"{idx}. Article ID : {article}")

            except requests.exceptions.Timeout:
                st.error("Erreur : Délai d’attente dépassé pour l'API.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erreur lors de l'appel à l'API : {e}")

# --- Footer ---
st.markdown(
    """
    <hr style="border:1px solid gray">
    <div style='text-align: center; color: gray; font-size: small;'>
        OpenClassrooms Projet 10 - MyContent | Développé par Vincent Dujardin | Formation Ingénieur IA - 2025
    </div>
    """,
    unsafe_allow_html=True
)
