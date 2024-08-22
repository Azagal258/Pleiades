### modules ###

import json
import requests
import os

### Function land ###

def ensure_dir_exists(dir_path: str):
    """
    Makes a dir, if it doesn't exist

    Parameters :
    dir_path (str) : path to dir

    Output :
    A fancy new dir, if needed (^-^)/
    """

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(f"Directory '{dir_path}' created.")

def ensure_file_exists(file_path: str):
    """
    Makes a file, if it doesn't exist

    Parameters :
    file_path (str) : path to files

    Output :
    A fancy new file, if needed (^-^)/
    """

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('0')
        print(f"File '{file_path}' created.")

def check_typo(group: str) -> str:
    """
    Ensures correct typo of groups

    Parameters :
    group (str) : name of the group

    Output :
    group_out (str) : formatted group name
    """

    if group.lower() in ["3s", "3 s", "triples", "triple s"]:
        group_out = "tripleS"
    else:
        group_out = group.lower()
    return group_out

def make_request(group: str, timestamp:str) -> json:
    """
    Will make a request to Nova api to return since the last time the code was run for a specific group

    Parameters :
    group (str) : the group name
    timestamp (str) : the value located in timestamp-*insert group*.txt

    Output :
    objekts (json) : json containing ids, fronts, and timestamps of all objekts requested
    """

    url = 'https://squid.subsquid.io/cosmo/graphql'
    query = f'''
    query MyQuery {{
        collections(where: {{ artists_containsAll: "{group}", timestamp_gt: "{timestamp}" }})  
        {{
        id
        front
        timestamp
        }}
    }}
    '''

    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://nova.gd'
    }
    data = {'query': query}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        try:
            objekts = response.json()['data']['collections']
        except Exception as e:
            print(e)
    return objekts

def get_all_values_by_key(data: json, target_key: str, results=None) -> list:
    """
    Find all values tied to a specific key in the given json

    Parameters :
    data (json) : The json containing all data
    target_key (str) : The key from which all values will be extracted from

    Output :
    result (list) : The list containing all data of a given key
    """

    if results is None:
        results = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                results.append(value)
            elif isinstance(value, (dict, list)):
                get_all_values_by_key(value, target_key, results)
    elif isinstance(data, list):
        for item in data:
            get_all_values_by_key(item, target_key, results)
    
    return results

def download_objekts(group, id, front):
    """
    Downloads all objekts requested and puts them into the adapted folder

    Parameters :
    group (str) : formatted group name
    id (list) : all names of pictures
    front (list) : all URL to get pictures from

    Output :
    A fancy new batch of pic (^-^)/
    """
    
    cnt = 0
    for i in range(len(id)):

        # File path where the image will be saved
        file_path = f'{group}/{id[i]}.png'

        # Send a GET request to the URL
        response = requests.get(front[i])

        # Check if the request was successful
        if response.status_code == 200:
            # Open the image using PIL
            with open(file_path, 'wb') as f:
                f.write(response.content)
            cnt += 1
            if cnt%10 == 0 :
                print(f"{cnt} images downloaded")
        else:
            print(f"Failed to retrieve file. Status code: {response.status_code}")

### Process ###

# Create dirs
ensure_dir_exists('./artms')
ensure_dir_exists('./tripleS')

# Create timestamps files
ensure_file_exists('timestamp-artms.txt')
ensure_file_exists('timestamp-tripleS.txt')

# Ensures correct typo
group = check_typo(input("Which group?\n"))

# Checks last most recent objekt's timestamp + Informs
with open(f"timestamp-{group}.txt", "r") as f:
    timestamp = f.read()
    print("Old timestamp : ", timestamp)

# gets JSON data from API
data = make_request(group, timestamp)

# Get all values for the specified keys
id = get_all_values_by_key(data, "id")
front = get_all_values_by_key(data, "front")
time = max(get_all_values_by_key(data, "timestamp"))

# General infos
print("New timestamp : ", time)
print("# of objekts : " , len(id))

# Saves new most recent objekt's timestamp
with open(f"timestamp-{group}.txt", "w") as f:
    f.write(time)

# Self explanatory
download_objekts(group, id, front)