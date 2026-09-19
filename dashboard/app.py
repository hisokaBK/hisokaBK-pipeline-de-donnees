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

