import requests
import os
import dotenv
import hashlib
import zipfile
from pathlib import Path
from typing import TypedDict
import sys

class AssetData(TypedDict):
    name: str
    digest: str
    browser_download_url: str

class ReleaseData(TypedDict):
    tag_name: str
    immutable: bool
    assets: list[AssetData]

__version__ = "v.0.1.0"

def sha256_file(path:str) -> str:
    """Check that the file hasn't been tampered with"""
    h = hashlib.sha256() 
    with open(path, "rb") as f: 
        for chunk in iter(lambda: f.read(8192), b""): 
            h.update(chunk) 
    return h.hexdigest()

def download_file(url: str, path: str, slug: str, timestamp:tuple[float, float]|None = None) -> bool:
    response = requests.get(url)
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch {slug} at {url} : Code {response.status_code}")
        return False
    
    with open(path, "wb") as f:
        f.write(response.content)
    if timestamp is not None:
        os.utime(path, timestamp)
    return True

def get_latest_release(is_update: bool) -> ReleaseData | None :
    """checks if there's a new release"""

    url = "https://api.github.com/repos/Azagal258/test-for-versioning/releases/latest"
    token = dotenv.get_key(".env", "gh_api_token")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    prefix = "Update check failed: " if is_update else ""

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] {prefix}Couldn't reach GitHub's API: {e}")
        return None

    try:
        data:ReleaseData = response.json()
    except Exception as e:
        print(f"[WARN] {prefix}Couldn't fetch latest release data : {e}")
        return None
    
    if is_update and "--force-update" in sys.argv:
        return data
    
    latest_version = data.get("tag_name")
    if latest_version and latest_version != __version__:
        print(
            f"[INFO] New version available: {__version__} -> {latest_version}\n"
            "[INFO] Run the script with flag '--update' to update"
        )
    elif not latest_version:
        print(
            "[WARN] Couldn't determine the latest release's version"
            "[WARN] Run with the flag --force-update to proceed without checking version" 
            "[WARN] Use only if the update system is broken. Manually verify releases before using"
        )

    if is_update:
        return data

    return None

def get_release_assets(data: ReleaseData) -> AssetData | None:
    update_package = None
    assets = data["assets"]

    if not assets:
        print("[ERROR] No assets found in the release")
        return None

    if "--force-update" in sys.argv:
        for asset in assets:
            if asset["name"].startswith("package") and asset["name"].endswith(".zip"):
                update_package = asset
                break
    else:
        latest_version = data["tag_name"]
        for asset in assets:
            if asset["name"] == f"package-{latest_version}.zip":
                update_package = asset
                break
    
    if not update_package:
        print("[ERROR] No valid package found in release assets")
        return None
    
    return update_package

def zip_safety_check(zip_path: str, dest_dir: str) -> None:
    dest = Path(dest_dir).resolve()

    with zipfile.ZipFile(zip_path, "r") as zip:
        for member in zip.infolist():
            target = (dest / member.filename).resolve()
            print(target)
            if not str(target).startswith(str(dest)):
                raise RuntimeError(f"Attempted zip-slip exploit: {member.filename}")
        zip.extractall(dest)

def extract_zip(zip_path: str):
    try :
        zip_safety_check(zip_path, "./update_temp/")
    except RuntimeError as RunE:
        print(f"{RunE}\nThat archive is not legit. Check sources")

def do_update():
    for file in os.listdir("./update_temp/"):
        try :
            os.replace(f"update_temp/{file}", file)
        except Exception as e:
            print(f"Failed to update {file} : {e}")
    os.rmdir("./update_temp/")


def main_update():
    dotenv.set_key(".env", "has_update_finished", "false")
    
    release_data = get_latest_release(True)
    if release_data is None :
        raise RuntimeError

    pacakge = get_release_assets(release_data)
    if pacakge is None :
        raise RuntimeError
    
    try :
        DL_url = pacakge["browser_download_url"]
        name = pacakge["name"]
        DL_path = f"./{name}"
        pacakge_hash = pacakge["digest"]
    except KeyError as e:
        raise RuntimeError(f"[ERROR] Can't get essential values from asset : {e}")

    if download_file(DL_url, DL_path, name):
    
        hash = sha256_file(name)
        gh_hash:str = pacakge_hash.split(":")[1]

        print(f"Calculated hash : {hash}")
        print(f"GH hash : {gh_hash}")

        is_expected_archive = (hash == gh_hash)
        if is_expected_archive:
            extract_zip(name)
            do_update()
        else:
            print("something failed...")

    print("Update finished, reminder to reboot")
    dotenv.set_key(".env", "has_update_finished", "true")

if __name__ == "__main__":
    try :
        main_update()
    except RuntimeError:
        print("[ERROR] Update failed")
        input("Press Enter to quit...")
        sys.exit()