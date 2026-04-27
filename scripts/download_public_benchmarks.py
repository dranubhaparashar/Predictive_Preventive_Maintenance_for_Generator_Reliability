"""
Utility script to download public benchmark datasets on your own machine.

This script is optional. The package already includes a runnable synthetic dataset.
"""

from pathlib import Path
from urllib.request import urlretrieve
import zipfile

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

URLS = {
    "ai4i_zip": "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip",
    "nasa_cmapss_zip": "https://data.nasa.gov/docs/legacy/CMAPSSData.zip",
    # FMUCD is hosted on Mendeley Data and may require manual download depending on availability.
    "fmucd_landing_page": "https://data.mendeley.com/datasets/cb8d2nsjss/1",
}

def download(url: str, destination: Path) -> None:
    print(f"Downloading: {url}")
    urlretrieve(url, destination)
    print(f"Saved to: {destination}")

def unzip(zip_path: Path, target_dir: Path) -> None:
    print(f"Extracting: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)
    print(f"Extracted to: {target_dir}")

def main() -> None:
    ai4i_zip = RAW / "ai4i.zip"
    nasa_zip = RAW / "CMAPSSData.zip"

    download(URLS["ai4i_zip"], ai4i_zip)
    unzip(ai4i_zip, RAW / "ai4i")

    download(URLS["nasa_cmapss_zip"], nasa_zip)
    unzip(nasa_zip, RAW / "nasa_cmapss")

    print("\nFMUCD note:")
    print("Visit the FMUCD landing page for manual download if needed:")
    print(URLS["fmucd_landing_page"])

if __name__ == "__main__":
    main()
