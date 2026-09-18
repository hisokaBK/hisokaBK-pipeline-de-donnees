import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


load_dotenv()


conn = psycopg.connect(
    host="localhost",
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)

print("Connexion à PostgreSQL réussie !")


with conn.cursor() as cursor:

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            city_id SERIAL PRIMARY KEY,
            city VARCHAR(100) NOT NULL,
            latitude DECIMAL(9, 6) NOT NULL,
            longitude DECIMAL(9, 6) NOT NULL,

            CONSTRAINT unique_city
                UNIQUE (city)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            forecast_id SERIAL PRIMARY KEY,
            city_id INTEGER NOT NULL,
            date DATE NOT NULL,
            temperature_max DECIMAL,
            temperature_min DECIMAL,
            precipitation DECIMAL,
            precipitation_probability_max DECIMAL,
            wind_speed_max DECIMAL,
            wind_gusts_max DECIMAL,
            weather_code INTEGER,

            CONSTRAINT fk_forecasts_city
                FOREIGN KEY (city_id)
                REFERENCES cities(city_id),

            CONSTRAINT unique_city_forecast
                UNIQUE (city_id, date)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            risk_id SERIAL PRIMARY KEY,
            forecast_id INTEGER NOT NULL,

            temperature_category VARCHAR(50),
            precipitation_category VARCHAR(50),
            wind_category VARCHAR(50),

            precipitation_score DECIMAL,
            wind_speed_score DECIMAL,
            wind_gusts_score DECIMAL,
            wind_score DECIMAL,
            temperature_score DECIMAL,

            risk_score DECIMAL
                CHECK (risk_score >= 0 AND risk_score <= 100),

            CONSTRAINT fk_risk_forecast
                FOREIGN KEY (forecast_id)
                REFERENCES forecasts(forecast_id),

            CONSTRAINT unique_forecast_risk
                UNIQUE (forecast_id)
        );
    """)


conn.commit()

print("Les tables sont prêtes !")


gold_df = pd.read_csv(
    "data/gold/weather_risk.csv"
)

print(
    f"Données Gold chargées : {len(gold_df)} lignes"
)


with conn.cursor() as cursor:

    villes = (
        gold_df[
            ["city", "latitude", "longitude"]
        ]
        .drop_duplicates(subset=["city"])
    )

    for _, ville in villes.iterrows():

        cursor.execute(
            """
            INSERT INTO cities (
                city,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s)

            ON CONFLICT (city)
            DO NOTHING
            """,
            (
                ville["city"],
                ville["latitude"],
                ville["longitude"]
            )
        )

    print(
        f"Villes traitées : {len(villes)}"
    )


conn.commit()



with conn.cursor() as cursor:

    for _, ligne in gold_df.iterrows():

        cursor.execute(
            """
            SELECT city_id
            FROM cities
            WHERE city = %s
            """,
            (ligne["city"],)
        )

        resultat = cursor.fetchone()

        if resultat is None:
            raise RuntimeError(
                f"Ville introuvable : {ligne['city']}"
            )

        city_id = resultat[0]

        cursor.execute(
            """
            INSERT INTO forecasts (
                city_id,
                date,
                temperature_max,
                temperature_min,
                precipitation,
                precipitation_probability_max,
                wind_speed_max,
                wind_gusts_max,
                weather_code
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )

            ON CONFLICT (city_id, date)
            DO UPDATE SET
                temperature_max = EXCLUDED.temperature_max,
                temperature_min = EXCLUDED.temperature_min,
                precipitation = EXCLUDED.precipitation,
                precipitation_probability_max =
                    EXCLUDED.precipitation_probability_max,
                wind_speed_max = EXCLUDED.wind_speed_max,
                wind_gusts_max = EXCLUDED.wind_gusts_max,
                weather_code = EXCLUDED.weather_code

            RETURNING forecast_id
            """,
            (
                city_id,
                ligne["date"],
                ligne["temperature_max"],
                ligne["temperature_min"],
                ligne["precipitation"],
                ligne["precipitation_probability_max"],
                ligne["wind_speed_max"],
                ligne["wind_gusts_max"],
                ligne["weather_code"]
            )
        )

        forecast_id = cursor.fetchone()[0]


        cursor.execute(
            """
            INSERT INTO risk_scores (
                forecast_id,
                temperature_category,
                precipitation_category,
                wind_category,
                precipitation_score,
                wind_score,
                temperature_score,
                risk_score
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )

            ON CONFLICT (forecast_id)
            DO UPDATE SET
                temperature_category =
                    EXCLUDED.temperature_category,
                precipitation_category =
                    EXCLUDED.precipitation_category,
                wind_category =
                    EXCLUDED.wind_category,
                precipitation_score =
                    EXCLUDED.precipitation_score,
                wind_score =
                    EXCLUDED.wind_score,
                temperature_score =
                    EXCLUDED.temperature_score,
                risk_score =
                    EXCLUDED.risk_score
            """,
            (
                forecast_id,
                ligne["temperature_category"],
                ligne["precipitation_category"],
                ligne["wind_category"],
                ligne["precipitation_score"],
                ligne["wind_score"],
                ligne["temperature_score"],
                ligne["risk_score"]
            )
        )


conn.commit()

print("Les données Gold ont été chargées avec succès !")


with conn.cursor() as cursor:

    cursor.execute(
        "SELECT COUNT(*) FROM cities"
    )
    nombre_villes = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM forecasts"
    )
    nombre_forecasts = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM risk_scores"
    )
    nombre_risks = cursor.fetchone()[0]


print(
    f"cities       : {nombre_villes}"
)

print(
    f"forecasts    : {nombre_forecasts}"
)

print(
    f"risk_scores  : {nombre_risks}"
)


conn.close()

print("Connexion PostgreSQL fermée.")