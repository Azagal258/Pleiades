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

FORCE_UPDATE = "--force-update" in sys.argv
UPDATE = "--update" in sys.argv

__version__ = "v.0.1.0"

def sha256_file(path:str) -> str:
    """Hashes a file to later check if it hasn't been tampered with
    
    Parameters
    ----------
    path : str
        Path to the file

    Returns
    -------
    hexdigest : str
        sha256 hash of the file
    """
    h = hashlib.sha256() 
    with open(path, "rb") as f: 
        for chunk in iter(lambda: f.read(8192), b""): 
            h.update(chunk) 
    return h.hexdigest()

def download_file(url: str, path: str, slug: str, timestamp:tuple[float, float]|None = None) -> bool:
    """Downloads the package for updating"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {slug} at {url} : {e}")
        return False
    
    with open(path, "wb") as f:
        f.write(response.content)
    if timestamp is not None:
        os.utime(path, timestamp)
    return True

def get_latest_release(is_update: bool) -> ReleaseData | None :
    """Fetches Github to get Pleiades's latest release's data
    
    Parameters
    ----------
    is_update : bool
        var to run the function in update-mode or normal mode
    
    Returns
    -------
    data : ReleaseData
        Github API response containing release data
    """

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
    
    if is_update and FORCE_UPDATE:
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
    """
    Parameters
    ----------
    data : ReleaseData
        Github API response containing release data 

    Returns
    -------
    update_package : AssetData
        Content required to fetch the update package 
    """
    update_package = None
    assets = data["assets"]

    if not assets:
        print("[ERROR] No assets found in the release")
        return None

    if FORCE_UPDATE:
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

def extract_zip(zip_path: str, dest_dir: str) -> None:
    """Extracts the archive to the designated location

    Parameters
    ----------
    zip_path: str
        path to the archive
    dest_dir: str
        path to decompress to
    """
    dest = Path(dest_dir).resolve()
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest)):
                raise RuntimeError(f"[CRITICAL] Attempted zip-slip exploit: {member.filename}")
        archive.extractall(dest)

def do_update() -> None:
    """Replaces old files with the contents from the update folder"""
    for file in os.listdir("./update_temp/"):
        try :
            os.replace(f"update_temp/{file}", file)
        except Exception as e:
            print(f"[ERROR] Failed to update {file} : {e}")
    
    if os.listdir("./update_temp/"):
        raise RuntimeError("[ERROR] Incomplete update")
    os.rmdir("./update_temp/")

def main_update():
    # To not run on partially updated contents
    dotenv.set_key(".env", "has_update_finished", "false")
    
    release_data = get_latest_release(True)
    if release_data is None :
        raise RuntimeError

    package = get_release_assets(release_data)
    if package is None :
        raise RuntimeError
    
    # Useful values
    DL_url = package["browser_download_url"]
    name = package["name"]
    DL_path = f"./{name}"
    package_hash = package["digest"]

    # If the download fails, stop everything
    if not download_file(DL_url, DL_path, name):
        raise RuntimeError 
    
    # Ensures no corruption of the file
    file_hash = sha256_file(name)
    algo, _, gh_hash = package_hash.partition(":")
    if algo != "sha256" or not gh_hash:
        raise RuntimeError("[ERROR] Unsupported digest format")

    print(f"Calculated hash : {file_hash}")
    print(f"GH hash : {gh_hash}")

    is_expected_archive = (file_hash == gh_hash)
    if not is_expected_archive:
        raise RuntimeError("[ERROR] File received doesn't match expected file. Aborting...")
    
    try :
        extract_zip(name, "./update_temp/")
    except RuntimeError as RunE:
        raise RuntimeError(f"{RunE}\n[ERROR] That archive is not legit, do not attempt to update with that release")

    do_update()


    print("Update finished, reminder to reboot")
    dotenv.set_key(".env", "has_update_finished", "true")

if __name__ == "__main__":
    try :
        main_update()
    except RuntimeError as e:
        print(
            f"{e}"
            "[ERROR] Update failed, please retry later"
        )
        input("Press Enter to quit...")
        sys.exit()