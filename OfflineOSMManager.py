import requests
from bs4 import BeautifulSoup
from pathlib import Path

download_path = Path("./osm-data")
download_path.mkdir(parents=True, exist_ok=True)

def download_manager(name, link):
    latest_url = ""
    req = requests.get(link)
    if req.status_code == 200:
        soup = BeautifulSoup(req.content, "html.parser")
        links = soup.find_all("a")
        for link in links:
            if link.get("href"):
                if "latest.osm" in link.get("href"):
                    latest_url = link.get("href")

    if latest_url != "":
        base_download_url = "https://download.geofabrik.de/europe/"
        download_url = base_download_url+latest_url
        print(download_url)

        target_file = f"{download_path/name}.osm.pbf"

        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            print("Beginning Download")

            total_size = int(r.headers.get("content-length", 0))
            downloaded = 0
            progress_percent = 0

            with open(target_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if total_size > 0:
                            progress_percent = round((downloaded / total_size) * 100, 2)
                            print(f"\rProgress: {progress_percent}%", end="", flush=True)
        print("\nDownload Complete")

    else:
        download_manager(name, link)

