import os
import pandas as pd
from google.cloud import bigquery, storage

BQ_SOURCE_PROJECT = "bigquery-public-data"
BQ_SOURCE_DATASET = "austin_bikeshare"
TABLES = ["bikeshare_trips", "bikeshare_stations"]

BUCKET_NAME = os.environ.get("BUCKET_NAME", "case-study-1-508412-raw-landing")
GCS_PREFIX = os.environ.get("GCS_PREFIX", "austin_bikeshare")


def extract_table_to_dataframe(bq_client: bigquery.Client, table_name: str) -> pd.DataFrame:
    """Queries the full public table and returns it as a pandas DataFrame."""
    query = f"SELECT * FROM `{BQ_SOURCE_PROJECT}.{BQ_SOURCE_DATASET}.{table_name}`"
    print(f"Querying {table_name}...")
    df = bq_client.query(query).to_dataframe()
    print(f"Retrieved {len(df)} rows from {table_name}.")
    return df


def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str):
    """Uploads the given local file to a GCS bucket."""
    print(f"Uploading {local_path} to gs://{bucket_name}/{blob_name}...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    print(f"Upload successful.")


def main():
    bq_client = bigquery.Client()

    for table_name in TABLES:
        df = extract_table_to_dataframe(bq_client, table_name)

        if df.empty:
            print(f"No data returned for {table_name}, skipping.")
            continue

        local_file = f"{table_name}.parquet"
        df.to_parquet(local_file, index=False)

        blob_name = f"{GCS_PREFIX}/{table_name}.parquet"
        upload_to_gcs(local_file, BUCKET_NAME, blob_name)


if __name__ == "__main__":
    main()