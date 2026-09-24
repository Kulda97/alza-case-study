CREATE OR REPLACE TABLE `case-study-1-508412.silver.bikes` AS
SELECT
    bike_id,
    manufacturer,
    CAST(price_eur AS NUMERIC) AS price_eur
FROM `case-study-1-508412.bronze.bikes`
WHERE bike_id IS NOT NULL
    AND price_eur IS NOT NULL
    AND CAST(price_eur AS NUMERIC) > 0
QUALIFY ROW_NUMBER() OVER (PARTITION BY bike_id ORDER BY _loaded_at DESC) = 1;

-- seventh row --> resolves the WRITE_APPEND from loading_to_bq.py
-- for every unique bike_id take ONLY the row from the last Cloud Run Job run
-- QUALIFY --> 176 duplicated rows per bike_id

-- in the following .sql queries i used the same procedure