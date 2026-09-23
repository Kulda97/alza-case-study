import os
from datetime import datetime, timezone

from google.cloud import bigquery

PROJECT_ID = os.environ.get("PROJECT_ID", "case-study-1-508412")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "case-study-1-508412-raw-landing")
BQ_DATASET = os.environ.get("BQ_DATASET", "bronze")

# mapping data sources in GCS bucket via their names to target the bronze layer
SOURCES = [
    {
        "gcs_path": "bikes_data.csv",
        "source_format": bigquery.SourceFormat.CSV,
        "table": "bikes",
    },
    {
        "gcs_path": "cnb_kurzy_2022_2023.csv",
        "source_format": bigquery.SourceFormat.CSV,
        "table": "cnb_rates",
    },
    {
        "gcs_path": "austin_weather_2022_2023.csv",
        "source_format": bigquery.SourceFormat.CSV,
        "table": "weather",
    },
    {
        "gcs_path": "austin_bikeshare/bikeshare_stations.parquet",
        "source_format": bigquery.SourceFormat.PARQUET,
        "table": "bikeshare_stations",
    },
    {
        "gcs_path": "austin_bikeshare/bikeshare_trips.parquet",
        "source_format": bigquery.SourceFormat.PARQUET,
        "table": "bikeshare_trips",
    },
]


def load_gcs_to_tmp(client: bigquery.Client, source: dict, run_timestamp: str) -> str:
    """Loads a raw GCS file into a temporary table with schema autodetect."""
    tmp_table = f"{PROJECT_ID}.{BQ_DATASET}._tmp_{source['table']}_{run_timestamp}"
    gcs_uri = f"gs://{BUCKET_NAME}/{source['gcs_path']}"

    job_config = bigquery.LoadJobConfig(
        source_format=source["source_format"],
        autodetect=True, # deriving the types of columns from CSV/Parquet
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # one-time operation in tmp table (truncate allowed)
    )
    if source["source_format"] == bigquery.SourceFormat.CSV: # header with column names
        job_config.skip_leading_rows = 1

    print(f"Loading {gcs_uri} into temp table {tmp_table}...")
    load_job = client.load_table_from_uri(gcs_uri, tmp_table, job_config=job_config) # same location: europe-west3
    load_job.result()  # wait for completion
    print(f"Tmp load finished ({load_job.output_rows} rows).")

    return tmp_table


def append_tmp_to_bronze(client: bigquery.Client, tmp_table: str, source: dict, gcs_path: str):
    """Copies tmp data into the final bronze table, adding ingestion metadata, then appends."""
    target_table = f"{PROJECT_ID}.{BQ_DATASET}.{source['table']}"

    query = f"""
        INSERT INTO `{target_table}`
        SELECT
            *,
            CURRENT_TIMESTAMP() AS _loaded_at,
            '{gcs_path}' AS _source_file
        FROM `{tmp_table}`
    """

    print(f"Appending tmp data into {target_table}...")
    try:
        client.query(query).result()
    except Exception:
        # Target table doesn't exist yet (first run) -> create it directly from tmp + metadata
        print(f"{target_table} does not exist yet, creating it from tmp data...")
        create_query = f"""
            CREATE TABLE `{target_table}` AS
            SELECT
                *,
                CURRENT_TIMESTAMP() AS _loaded_at,
                '{gcs_path}' AS _source_file
            FROM `{tmp_table}`
        """
        client.query(create_query).result()

    print(f"Bronze table {target_table} updated.")


def cleanup_tmp(client: bigquery.Client, tmp_table: str):
    print(f"Dropping tmp table {tmp_table}...")
    client.delete_table(tmp_table, not_found_ok=True) # if the table is not already existing, the code won't stop


def main():
    client = bigquery.Client(project=PROJECT_ID)

    dataset_ref = bigquery.DatasetReference(PROJECT_ID, BQ_DATASET)
    client.create_dataset(dataset_ref, exists_ok=True)

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    for source in SOURCES:
        tmp_table = load_gcs_to_tmp(client, source, run_timestamp)
        try:
            append_tmp_to_bronze(client, tmp_table, source, source["gcs_path"])
        finally: # better -> if try failes, tmp table will be deleted anyway
            cleanup_tmp(client, tmp_table)

    print(f"\nAll sources loaded into bronze layer successfully.")


if __name__ == "__main__":
    main()