CREATE OR REPLACE TABLE `case-study-1-508412.silver.cnb_rates` AS
SELECT
    datum,
    TRIM(`země`) AS country,
    TRIM(`měna`) AS currency,
    CAST(`množství` AS NUMERIC) AS quantity,
    TRIM(`kód`) AS code,
    CAST(kurz AS NUMERIC) AS rate
FROM `case-study-1-508412.bronze.cnb_rates`
WHERE datum IS NOT NULL
    AND `kód` IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY datum, `kód` ORDER BY _loaded_at DESC) = 1;