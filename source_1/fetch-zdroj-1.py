import os
import subprocess
import pandas as pd
from google.cloud import storage

OUTPUT_FILE = "bikes_data.alza"
OUTPUT_CLEAN_FILE = "bikes_data.csv"
URL = os.environ["SOURCE_URL"]  # comes from Secret Manageru
BUCKET_NAME = os.environ["BUCKET_NAME"]
GCS_BLOB_NAME = os.environ.get("GCS_BLOB_NAME", "bikes_data.csv")


def download_file():
    """Downloading the file via curl / silent, show-error, output"""
    print(f"Downloading {OUTPUT_FILE} via curl -sSo...")
    curl_cmd = ["curl", "-s", "-S", "-o", OUTPUT_FILE, URL]

    try:
        subprocess.run(curl_cmd, check=True)
        print(f"Downloading successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error while downloading: {e}")
        raise


def check_file_emptiness(filepath: str):
    """Checking whether the downloaded file exists or is empty"""
    print(f"Checking the downloaded file: {filepath}...")
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        raise FileNotFoundError(f"File {filepath} was not downloaded or is empty.")
    print(f"File {filepath} exists and is not empty.")


def check_file_type(filepath: str):
    """Checking binary header of downloaded .alza file"""
    print(f"Checking the type of the downloaded file: {filepath}...")
    try:
        subprocess.run(["file", filepath], check=True)
        print(f"Checking successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error while checking file type: {e}")
        raise


def load_file(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, engine="python", sep=r"[,]", on_bad_lines="skip")
    df.to_csv(OUTPUT_CLEAN_FILE, index=False)
    return df


def upload_to_gcs(filepath: str, bucket_name: str, blob_name: str):
    """Uploading the cleaned CSV to GCS bucket"""
    print(f"Uploading {filepath} to gs://{bucket_name}/{blob_name}...")
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(filepath)
    print(f"Upload successful.")


def main():
    download_file()
    check_file_emptiness(OUTPUT_FILE)
    check_file_type(OUTPUT_FILE)
    load_file(OUTPUT_FILE)
    upload_to_gcs(OUTPUT_CLEAN_FILE, BUCKET_NAME, GCS_BLOB_NAME)


if __name__ == "__main__":
    main()