### modules ###

import json
import requests
import os

### Function land ###

def ensure_file_exists(file_path: str):
    """Create the timestamp files to avoid querying the entire DB each time"""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('1970-01-01T00:00:00.000Z')
        print(f"File '{file_path}' created.")

def parse_group_name() -> str:
    """Ensures that the correct formatting for processing"""

    group = input("Which group's Objetks do you want to download?\n")
    if group.lower() in ["3s", "3 s", "triples", "triple s"]:
        group_out = "triples"
    elif group.lower() == "artms":
        group_out = "artms"
    elif group.lower() == "idntt":
        group_out = "idntt"
    else:
        print("Group unknown, verify for any typo.")
        group_out = parse_group_name()
    return group_out

def fetch_objekt_data(group: str, timestamp:str) -> list:
    """Will make a request to Pulsar's API to return since the last time the code was run for a specific group

    Parameters
    ----------
    - group : str
        Name of the wanted group
    - timestamp : str
        The ISO 8601 date located in timestamp-*group*.txt

    Returns
    -------
    - objekts : json
        json containing names, front images, and timestamps of all objekts requested
    """

    url = 'https://api.pulsar.azagal.eu/graphql'
    query = f'''
    query MyQuery {{
        collections(where: {{ artist_eq: "{group}", createdAt_gt: "{timestamp}" }})  
        {{
        slug
        frontImage
        createdAt
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
    return objekts

def get_all_values_by_key(data: dict, target_key: str, results=None) -> list:
    """Find all values tied to a specific key in the given json

    Parameters
    ----------
    - data : json
        Result of the API request
    - target_key : str
        The key from which all values will be extracted from

    Returns :
    - result : list
        The list containing all data of a given key
    """

    if results is None:
        results = []
    
    for item in data:
        results.append(item[f"{target_key}"])
    
    return results

def download_objekts(group: str, objekt_list:dict) -> None:
    """Downloads all objekts requested and puts them into the adapted folder

    Parameters
    ----------
    group : str
        Name of the wanted group
    objekt_list : json
        json containing all the objekts to be processed (MUST include a slug and frontImage field).

    Returns
    -------
        A fancy new batch of pics (^-^)/
    """
    cnt = 0
    for objekt in objekt_list:
        file_path = f"{group}/{objekt['slug']}.png"
        
        response = requests.get(objekt['frontImage'])
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            cnt += 1
            if cnt%10 == 0:
                print(f"{cnt} images downloaded")
        else:
            print(f"Failed to fetch {objekt['slug']}. Error {response.status_code}")

def new_batch_prompt() -> None:
    reply = input("Download a new batch? (yes/no)\n")
    if reply.lower() in ["yes","y"]:
        main()
    elif reply.lower() in ["no","n"]:
        print("Shutting down...")
        exit()
    else:
        new_batch_prompt()

def main() -> None:
    # Ensures correct typo
    group = parse_group_name()
    
    # Create env
    os.makedirs(f'./{group}', exist_ok=True)
    ensure_file_exists(f'timestamp-{group}.txt')

    # Checks last most recent objekt's timestamp
    with open(f"timestamp-{group}.txt", "r") as f:
        timestamp = f.read()

    # gets JSON data from API
    data = fetch_objekt_data(group, timestamp)
    if data == []:
        print("No new Objekts to download, try again later.")
        new_batch_prompt()

    # General informations
    print("Old timestamp : ", timestamp)
    time = max([entry["createdAt"] for entry in data])
    print("New timestamp : ", time)
    print("# of objekts : " , len(data))

    # Saves new most recent objekt's timestamp
    with open(f"timestamp-{group}.txt", "w") as f:
        f.write(time)

    download_objekts(group, data)
    print("Download finished")

    new_batch_prompt()

### Process ###

if __name__ == '__main__':
    main()