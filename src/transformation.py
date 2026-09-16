import pandas as pd
import json

cities = pd.read_csv('data/bronze/cities.csv')

with open("data/bronze/weather.json" , 'r' , encoding='utf-8') as fichier :
    weather = json.load(fichier)


weather_rows = []

for i, data in enumerate(weather):

    ville = cities.iloc[i]

    daily = data["daily"]

    for j in range(len(daily["time"])):
        weather_rows.append({
            "city": ville["city"],
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            "date": daily["time"][j],
            "temperature_max": daily["temperature_2m_max"][j],
            "temperature_min": daily["temperature_2m_min"][j],
            "precipitation": daily["precipitation_sum"][j]
        })

weather_df = pd.DataFrame(weather_rows)

#Standardiser les types et les dates-------------
weather_df["date"] = pd.to_datetime(weather_df["date"])
#print(weather_df.dtypes)

#detecter les doublons----------------
doublons = weather_df.duplicated(
    subset=["city", "date"]
)
print("Nombre de doublons :", doublons.sum())

#detecter les incoherences
temperature_incoherente = (
    weather_df["temperature_min"] > weather_df["temperature_max"]
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


latitude_incoherente = (
    (weather_df["latitude"] < -90) |
    (weather_df["latitude"] > 90)
)

longitude_incoherente = (
    (weather_df["longitude"] < -180) |
    (weather_df["longitude"] > 180)
)

print("Latitudes incohérentes :", latitude_incoherente.sum())
print("Longitudes incohérentes :", longitude_incoherente.sum())


print("Valeurs manquantes :" , weather_df.isna().sum())

print("Nombre de lignes :", len(weather_df))
print("Nombre de villes :", weather_df["city"].nunique())
print("Colonnes :", weather_df.columns.tolist())


#Exporter data csv
weather_df.to_csv(
    "data/silver/weather_clean.csv",
    index=False
)