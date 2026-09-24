CREATE OR REPLACE TABLE `case-study-1-508412.gold.4a` AS

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
  AND (LOWER(t.bike_type) LIKE '%electric%' OR LOWER(t.bike_type) LIKE '%e-bike%');
