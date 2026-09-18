--Quelles villes auront les températures les plus élevées

SELECT
    c.city,
    MAX(f.temperature_max) AS temperature_max
FROM cities c
JOIN forecasts f
    ON c.city_id = f.city_id
GROUP BY c.city
ORDER BY temperature_max DESC;

-- Villes avec les plus fortes précipitations

SELECT
    c.city,
    MAX(f.precipitation) AS precipitation_max
FROM cities c
JOIN forecasts f
    ON c.city_id = f.city_id
GROUP BY c.city
ORDER BY precipitation_max DESC;

-- Villes avec le risque moyen le plus élevé

SELECT
    c.city,
    ROUND(AVG(r.risk_score), 2) AS risque_moyen
FROM cities c
JOIN forecasts f
    ON c.city_id = f.city_id
JOIN risk_scores r
    ON f.forecast_id = r.forecast_id
GROUP BY c.city
ORDER BY risque_moyen DESC;

-- Périodes avec le risque maximal

SELECT
    c.city,
    f.date,
    r.risk_score
FROM cities c
JOIN forecasts f
    ON c.city_id = f.city_id
JOIN risk_scores r
    ON f.forecast_id = r.forecast_id
ORDER BY r.risk_score DESC
LIMIT 10;

-- Pour chaque ville, sa période avec le plus grand risque

SELECT
    city,
    date,
    risk_score
FROM (
    SELECT
        c.city,
        f.date,
        r.risk_score,
        ROW_NUMBER() OVER (
            PARTITION BY c.city
            ORDER BY r.risk_score DESC
        ) AS rang
    FROM cities c
    JOIN forecasts f
        ON c.city_id = f.city_id
    JOIN risk_scores r
        ON f.forecast_id = r.forecast_id
) AS classement
WHERE rang = 1
ORDER BY risk_score DESC;