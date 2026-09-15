import pandas as pd
import requests
import json

get_csv_info = pd.read_csv("data/bronze/cities.csv")

url_meteo = "https://api.open-meteo.com/v1/forecast"

weather_data = []

for _, ville in get_csv_info.iterrows():
 try :
   latitude  = ville['lat'] 
   longitude = ville['lng']
   nom_ville = ville['city']
   
   params = {
       "latitude": latitude,
       "longitude": longitude,
       "daily": [
           "temperature_2m_max",
           "temperature_2m_min",
           "precipitation_sum"
       ],
       "forecast_days": 7
   }
   
   response = requests.get( url_meteo, params=params ,timeout=5)
   response.raise_for_status()
   data = response.json()

   weather_data.append({
         "city": nom_ville,
         "weather": data
     })
   
 
 except requests.exceptions.Timeout :
     print("Erreur : le délai d'attente de la requête est dépassé.")
 except requests.exceptions.HTTPError as e :
     print("Erreur HTTP :", e)
 except requests.exceptions.RequestException as e:
     print("Erreur de requête :", e)
 except ValueError:
     print("Erreur : la réponse reçue n'est pas un JSON valide.")
 except Exception as e :
     print(f'erreur inattendu in api mto : {e}')

 
with open("data/bronze/weather.json", "w", encoding="utf-8") as fichier:
    json.dump(
        weather_data,
        fichier,
        ensure_ascii=False,
        indent=4
    )
 
print("Les données météo brutes ont été sauvegardées dans data/bronze/weather.json")
 
 