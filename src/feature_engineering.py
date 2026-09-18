import pandas as pd

weather_df = pd.read_csv(
    "data/silver/weather_clean.csv"
)

def categoriser_temperature(temperature):

    if temperature < 5:
        return "Très froid"

    elif temperature < 15:
        return "Froid"

    elif temperature < 25:
        return "Normal"

    elif temperature < 35:
        return "Chaud"

    else:
        return "Très chaud"


def categoriser_precipitation(precipitation):

    if precipitation == 0:
        return "Aucune"

    elif precipitation < 5:
        return "Faible"

    elif precipitation <= 20:
        return "Modérée"

    else:
        return "Forte"


def categoriser_vent(wind_speed):

    if wind_speed < 20:
        return "Faible"

    elif wind_speed < 40:
        return "Modéré"

    elif wind_speed <= 60:
        return "Fort"

    else:
        return "Très fort"


weather_df["temperature_category"] = (
    weather_df["temperature_max"]
    .apply(categoriser_temperature)
)

weather_df["precipitation_category"] = (
    weather_df["precipitation"]
    .apply(categoriser_precipitation)
)

weather_df["wind_category"] = (
    weather_df["wind_speed_max"]
    .apply(categoriser_vent)
)


def calculer_score_precipitation(precipitation):

    if precipitation == 0:
        return 0

    elif precipitation < 5:
        return 20

    elif precipitation <= 20:
        return 50

    elif precipitation <= 40:
        return 80

    else:
        return 100

def calculer_score_vent(wind_speed):

    if wind_speed < 20:
        return 0

    elif wind_speed < 40:
        return 30

    elif wind_speed <= 60:
        return 70

    else:
        return 100

def calculer_score_temperature(temperature):

    if 15 <= temperature < 25:
        return 0

    elif 5 <= temperature < 15:
        return 30

    elif 25 <= temperature < 35:
        return 30

    elif temperature < 5:
        return 70

    else:
        return 100

weather_df["precipitation_score"] = (
    weather_df["precipitation"]
    .apply(calculer_score_precipitation)
)

weather_df["wind_score"] = (
    weather_df["wind_speed_max"]
    .apply(calculer_score_vent)
)

weather_df["temperature_score"] = (
    weather_df["temperature_max"]
    .apply(calculer_score_temperature)
)

# ------> 40% precipitation  ---> 30% Vent  ---> 30% Température

weather_df["risk_score"] = (
    weather_df["precipitation_score"] * 0.40
    + weather_df["wind_score"] * 0.30
    + weather_df["temperature_score"] * 0.30
)


weather_df.to_csv(
    "data/gold/weather_risk.csv",
    index=False
)

print(
    "\nLes données Gold ont été sauvegardées "
)