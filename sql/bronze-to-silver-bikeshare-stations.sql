CREATE OR REPLACE TABLE `case-study-1-508412.silver.bikeshare_stations` AS
SELECT
    station_id,
    name,
    LOWER(TRIM(status)) AS status,
    address
FROM `case-study-1-508412.bronze.bikeshare_stations`
WHERE station_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY station_id ORDER BY _loaded_at DESC) = 1;