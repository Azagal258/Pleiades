### modules ###

import json
import requests
import os
from datetime import datetime, timezone
import dotenv

### Function land ###

def ensure_timestamp(env_path: str, group: str):
    """Verfies that the .env holds the group's timestamp. If not,\\
    generates a default value"""
    if dotenv.get_key(env_path, f"{group}") == None:
        print("Generating default timestamp")
        dotenv.set_key(env_path, f"{group}", '1970-01-01T00:00:00.000Z')

def parse_group_name() -> str:
    """Ensures that the correct formatting for processing"""

    while True:
        group = input("Which group's Objetks do you want to download?\n")
        if group.lower() in ["3s", "3 s", "triples", "triple s"]:
            return "triples"
        elif group.lower() == "artms":
            return "artms"
        elif group.lower() == "idntt":
            return "idntt"
        else:
            print("Group unknown, verify for any typo.")

def fetch_objekt_data(group: str, timestamp:str) -> list[dict]:
    """Requests Pulsar's API for all new Objekts since the last run

    Parameters
    ----------
    - group : str
        Name of the wanted group
    - timestamp : str
        The ISO 8601 date located in timestamp-*group*.txt

    Returns
    -------
    - objekts : json
        API response containing the new objekts
    """

    url = 'https://api.pulsar.azagal.eu/graphql'
    query = f'''
    query MyQuery {{
        collections(where: {{ artist_eq: "{group}", createdAt_gt: "{timestamp}" }})  
        {{
        slug
        frontImage
        createdAt
        member
        class
        season
        }}
    }}
    '''

    headers = {
        'Content-Type': 'application/json'
    }
    data = {'query': query}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        try:
            objekts = response.json()['data']['collections']
        except Exception as e:
            print(e)
            if input("Error while fetching objekt data, do you still want to proceed?").lower() in ["y", "ye", "yes"]:
                objekts = []
            else:
                exit()
    return objekts

def extract_unique_attributes(data: list[dict]) -> tuple[list] :
    """
    Extracts the members and seasons contained in data

    Parameters
    ----------
    data : json
        API response containing the new objekts
    
    Returns
    -------
    _ : tuple[list]
        A tuple containing :
        - the list containing all members, without duplicates
        - the list containing all seasons, without duplicates
    """
    members = set()
    seasons = set()

    for entry in data:
        members.add(entry["member"])
        seasons.add(entry["season"])
    
    members_list = list(members)
    seasons_list = list(seasons)

    return members_list, seasons_list

def create_sort_folders(unique_attribs: tuple[list], group: str, member_S_number: dict) -> None:
    """
    Parameters
    ----------
    unique_attribs : tuple[list]
        A tuple containing :
        - the list containing all members, without duplicates
        - the list containing all seasons, without duplicates
    group : str
        The name of the requested group
    member_S_number : dict
        A dict matching all S/id numbers for tripleS and idntt
    """
    for season in unique_attribs[1]:
        for member in unique_attribs[0]:
            try:
                path = f'./{group}/{season}/{member_S_number[member]}-{member}'
            except KeyError:
                if group in ("triples", "idntt"):
                    print(f"""
                        Can't find {member} S/id number. Ignoring S/id number for folder creation.\n
                        Ignore this message if it's a special objekt not tied to a member's name (i.e "S24" or "Icarus")
                        """)
                path = f'./{group}/{season}/{member}'
            os.makedirs(path, exist_ok=True)

def download_objekts(group: str, objekt_list:list[dict], member_S_number: dict) -> None:
    """Downloads all objekts requested and puts them into the adapted folder

    Parameters
    ----------
    group : str
        Name of the wanted group
    objekt_list : json
        json containing all the objekts to be processed
    member_S_number: dict
        A dict matching all S/id numbers for tripleS and idntt

    Returns
    -------
        A fancy new batch of pics (^-^)/
    """
    cnt = 0
    for objekt in objekt_list:
        member = objekt["member"]
        slug = objekt ["slug"]
        timestamp = (utime_timestamp(objekt['createdAt']))

        try:
            base_path = f'./{group}/{member_S_number[member]}-{member}'
        except KeyError:
            base_path = f'./{group}/{member}'

        # image handling #
        img_path = f"{base_path}/{slug}.png"
        if download_file(objekt['frontImage'], img_path, slug, timestamp):
            cnt += 1
            if cnt%10 == 0:
                print(f"{cnt} images downloaded")
        
        # MCOs handling #
        if objekt["class"] == 'Motion':
            video_url = f"https://cdn.apollo.cafe/mco/{slug}.mp4"
            video_path = f"{base_path}/{slug}.mp4"
            download_file(video_url, video_path, slug, timestamp)
            print("MCO video downloaded")

def download_file(url: str, path: str, slug: str, timestamp:tuple[float]|None = None) -> bool:
    """
    Parameters
    ----------
    url : str
        Url to objekt content
    path : str
        Path to save to
    slug : str
        Name of the objekt
    timestamp : tuple[float]
        Creation date of the objekt
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error {response.status_code}. Failed to fetch {slug} at {url}")
        return False
    
    with open(path, "wb") as f:
        f.write(response.content)
    if timestamp is not None:
        os.utime(path, timestamp)
    return True

def new_batch_prompt() -> None:
    reply = input("Download a new batch? (yes/no)\n")
    if reply.lower() in ["yes","y"]:
        main()
    elif reply.lower() in ["no","n"]:
        print("Shutting down...")
        exit()
    else:
        new_batch_prompt()

def utime_timestamp(timestamp : str) -> tuple[float]:
    """Convert an ISO timestamp to a UNIX timstamp"""
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    posixts = dt.timestamp()
    utimets = (posixts, posixts)
    return utimets

def main() -> None:
    member_S_number = {
        "SeoYeon" : "S1",
        "HyeRin" : "S2",
        "JiWoo" : "S3",
        "ChaeYeon" : "S4",
        "YooYeon" : "S5",
        "SooMin" : "S6",
        "NaKyoung" : "S7",
        "YuBin" : "S8",
        "Kaede" : "S9",
        "DaHyun" : "S10",
        "Kotone" : "S11",
        "YeonJi" : "S12",
        "Nien" : "S13",
        "SoHyun" : "S14",
        "Xinyu" : "S15",
        "Mayu" : "S16",
        "Lynn" : "S17",
        "JooBin" : "S18",
        "HaYeon" : "S19",
        "ShiOn" : "S20",
        "ChaeWon" : "S21",
        "Sullin" : "S22",
        "SeoAh" : "S23",
        "JiYeon" : "S24",
        "DoHun" : "id1",
        "HeeJu" : "id2",
        "MinGyeol" : "id3",
        "TaeIn" : "id4",
        "JaeYoung" : "id5",
        "JuHo" : "id6",
        "JiWoon" : "id7",
        "HwanHee" : "id8",
    }

    env_path = ".env"

    # Ensures correct typo
    group = parse_group_name()
    
    # Create env
    ensure_timestamp(env_path, group)

    # Checks last most recent objekt's timestamp
    timestamp = dotenv.get_key(".env", group)
    print("Old timestamp : ", timestamp)

    # gets JSON data from API
    data = fetch_objekt_data(group, timestamp)
    if data == []:
        print("No new Objekts to download, try again later.")
        new_batch_prompt()
    
    # Creates folders to sort per member
    unique_attribs = extract_unique_attributes(data)
    create_sort_folders(unique_attribs, group, member_S_number)

    # General informations
    time = max([entry["createdAt"] for entry in data])
    print("New timestamp : ", time)
    print("# of objekts : " , len(data))

    download_objekts(group, data, member_S_number)
    print("Download finished")

    # Saves new most recent objekt's timestamp
    dotenv.set_key(env_path, group, time)

    new_batch_prompt()

### Process ###

if __name__ == '__main__':
    main()