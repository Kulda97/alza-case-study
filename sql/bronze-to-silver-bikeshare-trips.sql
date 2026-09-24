CREATE OR REPLACE TABLE `case-study-1-508412.silver.bikeshare_trips` AS
SELECT
    trip_id,
    bike_id,
    bike_type,
    subscriber_type,
    start_time,
    start_station_id,
    start_station_name,
    end_station_id,
    end_station_name,
    duration_minutes
FROM `case-study-1-508412.bronze.bikeshare_trips`
WHERE trip_id IS NOT NULL
    AND bike_id IS NOT NULL
    AND duration_minutes > 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY trip_id ORDER BY _loaded_at DESC) = 1;