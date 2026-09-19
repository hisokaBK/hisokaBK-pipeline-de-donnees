import os

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Weather Risk Dashboard",
    page_icon="🌦️",
    layout="wide"
)


# ============================================================
# TITRE
# ============================================================

st.title("🌦️ Weather Risk Dashboard")

st.write(
    "Visualisation des prévisions météo et des risques "
    "pour les villes marocaines."
)


# ============================================================
# CONNEXION À POSTGRESQL
# ============================================================

try:

    conn = psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    st.success("Connexion à PostgreSQL réussie !")


except psycopg.Error as e:

    st.error(
        f"Impossible de se connecter à PostgreSQL : {e}"
    )

    st.stop()


# ============================================================
# RÉCUPÉRATION DES DONNÉES
# ============================================================

query = """
    SELECT
        c.city,
        f.date,
        f.temperature_max,
        f.temperature_min,
        f.precipitation,
        f.precipitation_probability_max,
        f.wind_speed_max,
        f.wind_gusts_max,
        f.weather_code,
        r.temperature_category,
        r.precipitation_category,
        r.wind_category,
        r.precipitation_score,
        r.wind_score,
        r.temperature_score,
        r.risk_score
    FROM cities c
    JOIN forecasts f
        ON c.city_id = f.city_id
    JOIN risk_scores r
        ON f.forecast_id = r.forecast_id
    ORDER BY c.city, f.date;
"""


try:

    df = pd.read_sql_query(
        query,
        conn
    )

    st.success(
        f"Données récupérées : {len(df)} lignes"
    )


except Exception as e:

    st.error(
        f"Erreur lors de la récupération des données : {e}"
    )

    conn.close()
    st.stop()


conn.close()


# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

df["date"] = pd.to_datetime(df["date"])


# ============================================================
# FILTRES
# ============================================================

st.sidebar.header("🎛️ Filtres")


# ------------------------------------------------------------
# 1. FILTRE VILLE
# ------------------------------------------------------------

villes = sorted(
    df["city"].unique().tolist()
)

ville_selectionnee = st.sidebar.selectbox(
    "🏙️ Ville",
    ["Toutes les villes"] + villes
)


# ------------------------------------------------------------
# 2. FILTRE DATE
# ------------------------------------------------------------

dates_disponibles = sorted(
    df["date"].dt.date.unique()
)

date_selectionnee = st.sidebar.selectbox(
    "📅 Date",
    ["Toutes les dates"] + dates_disponibles
)


# ------------------------------------------------------------
# 3. FILTRE PÉRIODE
# ------------------------------------------------------------

periode_selectionnee = st.sidebar.selectbox(
    "🗓️ Période",
    [
        "Toutes les périodes",
        "3 prochains jours",
        "5 prochains jours",
        "7 prochains jours"
    ]
)


# ------------------------------------------------------------
# 4. FILTRE NIVEAU DE RISQUE
# ------------------------------------------------------------

niveau_risque = st.sidebar.selectbox(
    "⚠️ Niveau de risque",
    [
        "Tous les niveaux",
        "Faible",
        "Modéré",
        "Élevé"
    ]
)


# ============================================================
# APPLICATION DES FILTRES
# ============================================================

df_filtre = df.copy()


# ------------------------------------------------------------
# Filtre ville
# ------------------------------------------------------------

if ville_selectionnee != "Toutes les villes":

    df_filtre = df_filtre[
        df_filtre["city"] == ville_selectionnee
    ]


# ------------------------------------------------------------
# Filtre date
# ------------------------------------------------------------

if date_selectionnee != "Toutes les dates":

    df_filtre = df_filtre[
        df_filtre["date"].dt.date == date_selectionnee
    ]


# ------------------------------------------------------------
# Filtre période
# ------------------------------------------------------------

if periode_selectionnee != "Toutes les périodes":

    nombre_jours = {
        "3 prochains jours": 3,
        "5 prochains jours": 5,
        "7 prochains jours": 7
    }

    jours = nombre_jours[periode_selectionnee]

    date_depart = df_filtre["date"].min()

    date_fin = date_depart + pd.Timedelta(
        days=jours - 1
    )

    df_filtre = df_filtre[
        (df_filtre["date"] >= date_depart)
        &
        (df_filtre["date"] <= date_fin)
    ]


# ------------------------------------------------------------
# Filtre niveau de risque
# ------------------------------------------------------------

if niveau_risque == "Faible":

    df_filtre = df_filtre[
        df_filtre["risk_score"] < 30
    ]


elif niveau_risque == "Modéré":

    df_filtre = df_filtre[
        (df_filtre["risk_score"] >= 30)
        &
        (df_filtre["risk_score"] < 50)
    ]


elif niveau_risque == "Élevé":

    df_filtre = df_filtre[
        df_filtre["risk_score"] >= 50
    ]

