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


# ============================================================
# VÉRIFICATION
# ============================================================

if df_filtre.empty:

    st.warning(
        "Aucune donnée ne correspond aux filtres sélectionnés."
    )

    st.stop()


# ============================================================
# KPI
# ============================================================

st.subheader("Indicateurs clés")


nombre_villes = df_filtre["city"].nunique()


temperature_max = df_filtre[
    "temperature_max"
].max()


precipitation_max = df_filtre[
    "precipitation"
].max()


nombre_periodes_risque = (
    df_filtre["risk_score"] >= 50
).sum()


ligne_risque_max = df_filtre.loc[
    df_filtre["risk_score"].idxmax()
]


ville_risque_max = ligne_risque_max["city"]


date_risque_max = ligne_risque_max["date"]


risk_max = ligne_risque_max["risk_score"]


# ============================================================
# AFFICHAGE DES KPI
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "🏙️ Nombre de villes",
        nombre_villes
    )


with col2:

    st.metric(
        "🌡️ Température maximale",
        f"{temperature_max:.1f} °C"
    )


with col3:

    st.metric(
        "🌧️ Précipitations maximales",
        f"{precipitation_max:.1f} mm"
    )


with col4:

    st.metric(
        "⚠️ Périodes à risque",
        nombre_periodes_risque
    )


with col5:

    st.metric(
        "📍 Risque le plus élevé",
        ville_risque_max,
        f"{risk_max:.1f} / 100"
    )


# ============================================================
# ALERTE PRINCIPALE
# ============================================================

st.subheader("🚨 Alerte principale")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "📍 Ville",
        ville_risque_max
    )


with col2:

    st.metric(
        "📅 Date",
        date_risque_max.strftime("%d/%m/%Y")
    )


with col3:

    st.metric(
        "⚠️ Risque",
        f"{risk_max:.1f} / 100"
    )


# ============================================================
# FACTEURS DU RISQUE
# ============================================================

st.write("### 🔎 Facteurs du risque")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🌧️ Risque précipitations",
        f"{ligne_risque_max['precipitation_score']:.1f}"
    )


with col2:

    st.metric(
        "💨 Risque vent",
        f"{ligne_risque_max['wind_score']:.1f}"
    )


with col3:

    st.metric(
        "🌡️ Risque température",
        f"{ligne_risque_max['temperature_score']:.1f}"
    )


# ============================================================
# INFORMATIONS GÉNÉRALES
# ============================================================

st.subheader("Données disponibles")


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Nombre de lignes",
        len(df_filtre)
    )


with col2:

    st.metric(
        "Nombre de villes",
        df_filtre["city"].nunique()
    )


with col3:

    st.metric(
        "Nombre de dates",
        df_filtre["date"].nunique()
    )


# ============================================================
# TABLEAU
# ============================================================

st.subheader("Prévisions météo et risques")


st.dataframe(
    df_filtre,
    use_container_width=True
)