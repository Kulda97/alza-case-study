import os
import requests
import pandas as pd
from google.cloud import storage

# Static date range (could be adjust)
START_DATE = "2022-12-20"
END_DATE = "2023-02-03"
LOCATION = "Austin,TX,USA"

API_KEY = os.environ["VISUAL_CROSSING_API_KEY"]  # comes from Secret Manager
BUCKET_NAME = os.environ.get("BUCKET_NAME", "case-study-1-508412-raw-landing")
OUTPUT_FILE = "austin_weather_2022_2023.csv"
GCS_BLOB_NAME = os.environ.get("GCS_BLOB_NAME", OUTPUT_FILE)

BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# cleaner mapping
COLUMN_MAPPING = {
    "datetime": "date",
    "tempmax": "temp_max_c",
    "tempmin": "temp_min_c",
    "temp": "temp_avg_c",
    "humidity": "humidity_pct",
    "precip": "precipitation_mm",
    "windspeed": "wind_speed_kmh",
}


def fetch_weather_data(location: str, start_date: str, end_date: str) -> dict:
    """Fetches historical daily weather data for a location and date range."""
    url = f"{BASE_URL}/{location}/{start_date}/{end_date}"
    params = {
        "unitGroup": "metric",  # EU location better than difficult transformations from US (TODO: good idea on validation)
        "key": API_KEY,
        "include": "days",
        "contentType": "json",
    }

    print(f"Fetching weather data for {location} from {start_date} to {end_date}...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def transform_weather_data(raw_data: dict) -> pd.DataFrame:
    """Selects and renames the key columns from the raw API response."""
    days = raw_data.get("days", [])
    if not days:
        return pd.DataFrame()

    df = pd.DataFrame(days)
    available_columns = [col for col in COLUMN_MAPPING if col in df.columns]
    df = df[available_columns].rename(columns=COLUMN_MAPPING)
    return df


def upload_to_gcs(filepath: str, bucket_name: str, blob_name: str):
    """Uploads the given local file to a GCS bucket."""
    print(f"Uploading {filepath} to gs://{bucket_name}/{blob_name}...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filepath)
    print(f"Upload successful.")


def main():
    raw_data = fetch_weather_data(LOCATION, START_DATE, END_DATE)
    weather_df = transform_weather_data(raw_data)

    if weather_df.empty:
        print(f"No weather records were returned.")
        return

    weather_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nDownloaded {len(weather_df)} daily records.")
    print(f"Data saved to file: {OUTPUT_FILE}")

    upload_to_gcs(OUTPUT_FILE, BUCKET_NAME, GCS_BLOB_NAME)


if __name__ == "__main__":
    main()