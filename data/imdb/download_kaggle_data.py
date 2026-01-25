import os
import json
import hashlib
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET = "harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows"
DOWNLOAD_PATH = "data/imdb"
CSV_NAME = "imdb_top_1000.csv"
METADATA_FILE = "metadata.json"

os.makedirs(DOWNLOAD_PATH, exist_ok=True)

csv_path = os.path.join(DOWNLOAD_PATH, CSV_NAME)
metadata_path = os.path.join(DOWNLOAD_PATH, METADATA_FILE)


def file_checksum(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def load_metadata():
    if not os.path.exists(metadata_path):
        return None
    with open(metadata_path, "r") as f:
        return json.load(f)


def save_metadata(checksum):
    metadata = {
        "checksum": checksum,
        "file_size": os.path.getsize(csv_path),
        "last_modified": os.path.getmtime(csv_path),
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


def should_download():
    if not os.path.exists(csv_path):
        return True

    metadata = load_metadata()
    if metadata is None:
        return True

    current_checksum = file_checksum(csv_path)

    if metadata["checksum"] != current_checksum:
        print("Dataset checksum changed.")
        return True

    return False


if should_download():
    print("Downloading IMDb dataset from Kaggle...")
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(DATASET, path=DOWNLOAD_PATH, unzip=True)
    print("Download complete.")

    checksum = file_checksum(csv_path)
    save_metadata(checksum)
else:
    print("Dataset is up to date. Skipping download.")