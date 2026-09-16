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

print(weather_df.dtypes)
weather_df["date"] = pd.to_datetime(weather_df["date"])
print(weather_df.dtypes)


