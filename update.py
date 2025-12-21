import requests
import os
import dotenv
import hashlib
import zipfile
from pathlib import Path

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

def get_latest_package() -> dict:

    url = "https://api.github.com/repos/Azagal258/test-for-versioning/releases/latest"
    headers = {
        "Accept" : "application/vnd.github+json",
        "Authorization" : f"Bearer {dotenv.get_key(".env", "gh_api_token")}"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    is_immutable = data["immutable"]
    if is_immutable:
        latest_version = data["tag_name"]
        for asset in data["assets"]:
            if asset["name"] == f"package-{latest_version}.zip":
                update_package = asset
                break
    else:
        pass
    
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

def main():
    dotenv.set_key(".env", "has_update_finished", "false")
    package = get_latest_package()
    
    DL_url = package["browser_download_url"]
    name = package["name"]
    DL_path = f"./{name}"

    if download_file(DL_url, DL_path, name):
    
        hash = sha256_file(name)
        gh_hash = package["digest"].split(":")[1]

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
    main()
