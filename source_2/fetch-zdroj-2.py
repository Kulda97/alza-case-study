import io
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from google.cloud import storage

# Static test range (could be adjust)
START_DATE = "2022-12-20"
END_DATE = "2023-02-03"
OUTPUT_FILE = "cnb_kurzy_2022_2023.csv"

BUCKET_NAME = os.environ.get("BUCKET_NAME", "case-study-1-508412-raw-landing")
GCS_BLOB_NAME = os.environ.get("GCS_BLOB_NAME", OUTPUT_FILE)


def download_cnb_rates(start_date_str: str, end_date_str: str) -> pd.DataFrame:
    """Downloads CNB rates for the given date range."""
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

    all_data = []

    current_date = start_date
    while current_date <= end_date:
        date_formatted = current_date.strftime("%d.%m.%Y")
        url = f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date={date_formatted}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            text_content = response.text
            lines = text_content.strip().split("\n")

            if len(lines) > 2:
                df_day = pd.read_csv(io.StringIO("\n".join(lines[1:])), sep="|")
                df_day["datum"] = current_date
                df_day["kurz"] = (
                    df_day["kurz"].astype(str).str.replace(",", ".").astype(float)
                )

                all_data.append(df_day)

        except requests.RequestException as e:
            print(f"Error while downloading data for date {date_formatted}: {e}")

        current_date += timedelta(days=1)

    if not all_data:
        return pd.DataFrame()

    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df[["datum", "země", "měna", "množství", "kód", "kurz"]]

    return final_df


def upload_to_gcs(filepath: str, bucket_name: str, blob_name: str):
    """Uploads the given local file to a GCS bucket."""
    print(f"Uploading {filepath} to gs://{bucket_name}/{blob_name}...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filepath)
    print(f"Upload successful.")


def main():
    print(f"Downloading CNB data from {START_DATE} to {END_DATE}...")
    rates_df = download_cnb_rates(START_DATE, END_DATE)

    if rates_df.empty:
        print(f"No records were downloaded.")
        return

    # utf-8-sig encoding ensures correct display of Czech characters e.g. in Excel
    rates_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\nDownloaded {len(rates_df)} records in total.")
    print(f"Data successfully saved to file: {OUTPUT_FILE}")

    upload_to_gcs(OUTPUT_FILE, BUCKET_NAME, GCS_BLOB_NAME)


if __name__ == "__main__":
    main()