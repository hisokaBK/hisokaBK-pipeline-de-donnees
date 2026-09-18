import pandas as pd
import requests
import json


cities = pd.read_csv("data/bronze/cities.csv")

url_meteo = "https://api.open-meteo.com/v1/forecast"

weather_data = []


for _, ville in cities.iterrows():

    try:

        latitude = ville["lat"]
        longitude = ville["lng"]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "weather_code"
            ],
            "forecast_days": 7
        }

        response = requests.get(
            url_meteo,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        # نخزنو غير response الخام ديال API
        weather_data.append(data)

        print(f"OK : {ville['city']}")

    except requests.exceptions.Timeout:

        raise RuntimeError(
            f"Timeout pour la ville : {ville['city']}"
        )

    except requests.exceptions.HTTPError as e:

        raise RuntimeError(
            f"Erreur HTTP pour {ville['city']} : {e}"
        )

    except requests.exceptions.RequestException as e:

        raise RuntimeError(
            f"Erreur de requête pour {ville['city']} : {e}"
        )

    except ValueError:

        raise RuntimeError(
            f"Erreur JSON pour {ville['city']}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Erreur inattendue pour {ville['city']} : {e}"
        )


if len(weather_data) != len(cities):

    raise RuntimeError(
        "Le nombre de réponses météo ne correspond pas "
        "au nombre de villes."
    )

with open(
    "data/bronze/weather.json",
    "w",
    encoding="utf-8"
) as fichier:

    json.dump(
        weather_data,
        fichier,
        ensure_ascii=False,
        indent=4
    )


print(
    "Les données météo brutes ont été sauvegardées "
)