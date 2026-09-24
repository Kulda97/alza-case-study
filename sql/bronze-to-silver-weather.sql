CREATE OR REPLACE TABLE `case-study-1-508412.silver.weather` AS
SELECT
    CAST(date AS DATE) AS date,
    temp_max_c,
    temp_min_c,
    temp_avg_c,
    humidity_pct,
    precipitation_mm,
    wind_speed_kmh
FROM `case-study-1-508412.bronze.weather`
WHERE date IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY date ORDER BY _loaded_at DESC) = 1;