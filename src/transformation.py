import pandas as pd
import json


cities = pd.read_csv(
    "data/bronze/cities.csv"
)


with open(
    "data/bronze/weather.json",
    "r",
    encoding="utf-8"
) as fichier:

    weather = json.load(fichier)


weather_rows = []


# join
for i, data in enumerate(weather):

    ville = cities.iloc[i]

    daily = data["daily"]

    for j in range(len(daily["time"])):

        weather_rows.append({

            "city": ville["city"],

            "latitude": data["latitude"],

            "longitude": data["longitude"],

            "date": daily["time"][j],

            "temperature_max":
                daily["temperature_2m_max"][j],

            "temperature_min":
                daily["temperature_2m_min"][j],

            "precipitation":
                daily["precipitation_sum"][j],

            "precipitation_probability_max":
                daily["precipitation_probability_max"][j],

            "wind_speed_max":
                daily["wind_speed_10m_max"][j],

            "wind_gusts_max":
                daily["wind_gusts_10m_max"][j],

            "weather_code":
                daily["weather_code"][j]

        })


weather_df = pd.DataFrame(weather_rows)


# Standardiser les types et les dates ----------------

weather_df["date"] = pd.to_datetime(
    weather_df["date"]
)


# Détecter les doublons ----------------

doublons = weather_df.duplicated(
    subset=["city", "date"]
)

print(
    "Nombre de doublons :",
    doublons.sum()
)


# Détecter les incohérences ----------------

temperature_incoherente = (
    weather_df["temperature_min"]
    > weather_df["temperature_max"]
)

print(
    "Températures incohérentes :",
    temperature_incoherente.sum()
)


precipitation_incoherente = (
    weather_df["precipitation"] < 0
)

print(
    "Précipitations négatives :",
    precipitation_incoherente.sum()
)


probabilite_incoherente = (
    (weather_df["precipitation_probability_max"] < 0)
    |
    (weather_df["precipitation_probability_max"] > 100)
)

print(
    "Probabilités de précipitation incohérentes :",
    probabilite_incoherente.sum()
)


wind_speed_incoherente = (
    weather_df["wind_speed_max"] < 0
)

print(
    "Vitesses de vent incohérentes :",
    wind_speed_incoherente.sum()
)


wind_gusts_incoherente = (
    weather_df["wind_gusts_max"] < 0
)

print(
    "Rafales de vent incohérentes :",
    wind_gusts_incoherente.sum()
)


weather_code_incoherent = (
    weather_df["weather_code"] < 0
)

print(
    "Weather codes incohérents :",
    weather_code_incoherent.sum()
)


latitude_incoherente = (
    (weather_df["latitude"] < -90)
    |
    (weather_df["latitude"] > 90)
)

longitude_incoherente = (
    (weather_df["longitude"] < -180)
    |
    (weather_df["longitude"] > 180)
)

print(
    "Latitudes incohérentes :",
    latitude_incoherente.sum()
)

print(
    "Longitudes incohérentes :",
    longitude_incoherente.sum()
)


# Contrôle de qualité ----------------

print(
    "Valeurs manquantes :",
    weather_df.isna().sum()
)

print(
    "Nombre de lignes :",
    len(weather_df)
)

print(
    "Nombre de villes :",
    weather_df["city"].nunique()
)

print(
    "Colonnes :",
    weather_df.columns.tolist()
)


# Exporter les données nettoyées ----------------

weather_df.to_csv(
    "data/silver/weather_clean.csv",
    index=False
)

print(
    "Les données nettoyées ont été sauvegardées "
)