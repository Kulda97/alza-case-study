CREATE OR REPLACE TABLE `case-study-1-508412.gold.4b` AS

WITH original_4a AS (
  SELECT
    DATE(t.start_time) AS trip_date,
    t.start_station_name,
    t.bike_id,
    ROUND(t.duration_minutes / 60.0, 2) AS duration_hours
  FROM `case-study-1-508412.silver.bikeshare_trips` AS t


-- JOIN for verification of start_station, plus 'active'
  JOIN `case-study-1-508412.silver.bikeshare_stations` AS s1
    ON CAST(t.start_station_id AS STRING) = CAST(s1.station_id AS STRING)
    AND LOWER(s1.status) = 'active'


-- JOIN for verification of end_station, plus 'active'
  JOIN `case-study-1-508412.silver.bikeshare_stations` AS s2
    ON CAST(t.end_station_id AS STRING) = CAST(s2.station_id AS STRING)
    AND LOWER(s2.status) = 'active'

  WHERE
    LOWER(t.start_station_name) = LOWER(t.end_station_name)
    AND (LOWER(t.bike_type) LIKE '%electric%' OR LOWER(t.bike_type) LIKE '%e-bike%')
)

SELECT
  o.trip_date,
  o.start_station_name,
  o.bike_id,
  o.duration_hours,
  w.temp_avg_c,
  b.manufacturer,
  b.price_eur,
  c.rate AS cnb_eur_rate,
  ROUND(b.price_eur * (c.rate / c.quantity), 2) AS price_czk
FROM original_4a AS o

LEFT JOIN `case-study-1-508412.silver.weather` AS w
  ON o.trip_date = w.date

LEFT JOIN `case-study-1-508412.silver.bikes` AS b
  ON o.bike_id = b.bike_id

LEFT JOIN `case-study-1-508412.silver.cnb_rates` AS c
  ON o.trip_date = c.datum
  AND LOWER(c.code) = 'eur'

-- well, i eventually found out, that a lot of rows of temp_avg_c and cnb_eur_rate are EMPTY (yeah, becuase of that I downloaded data only in specified time range)
-- TODO: another run with wider time range

-- test run to show some NOT NULL cnb_eur_rate and temp_avg_c

--SELECT * FROM `case-study-1-508412.gold.4b`
--WHERE cnb_eur_rate IS NOT NULL AND temp_avg_c IS NOT NULL
--LIMIT 5;
