import os

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
            longitude DECIMAL(9, 6) NOT NULL
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

print("Les tables ont été créées avec succès !")



conn.close()