### modules ###

import json
import requests
import os

### Function land ###

def ensure_file_exists(file_path: str):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            f.write('0')
        print(f"File '{file_path}' created.")

def parse_group_name(group: str) -> str:
    """Ensures that the correct formatting for processing"""

    if group.lower() in ["3s", "3 s", "triples", "triple s"]:
        group_out = "tripleS"
    else:
        group_out = group.lower()
    return group_out

def fetch_objekt_data(group: str, timestamp:str) -> json:
    """
    Will make a request to Nova api to return since the last time the code was run for a specific group

    Parameters :
    group (str) : the group name
    timestamp (str) : the value located in timestamp-*insert group*.txt

    Output :
    objekts (json) : json containing ids, fronts, and timestamps of all objekts requested
    """

    url = 'https://cosmo-api.gillespie.eu/graphql'
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
            with open(file_path, 'wb') as f:
                f.write(response.content)
            cnt += 1
            if cnt%10 == 0 :
                print(f"{cnt} images downloaded")
        else:
            print(f"Failed to retrieve file. Status code: {response.status_code}")

### Process ###

if __name__ == '__main__':
    
    # Ensures correct typo
    group = parse_group_name(input("Which group?\n"))
    
    # Create env
    os.makedirs(f'./{group}', exist_ok=True)
    ensure_file_exists(f'timestamp-{group}.txt')

    # Checks last most recent objekt's timestamp + Informs
    with open(f"timestamp-{group}.txt", "r") as f:
        timestamp = f.read()

    # gets JSON data from API
    data = fetch_objekt_data(group, timestamp)
    if data == []:
        print("No new Objekts to download, try again later")
        input("Press Enter to quit...")
        exit()

    print("Old timestamp : ", timestamp)
    id = get_all_values_by_key(data, "id")
    front = get_all_values_by_key(data, "front")
    time = max(get_all_values_by_key(data, "timestamp"))

    print("New timestamp : ", time)
    print("# of objekts : " , len(id))

    # Saves new most recent objekt's timestamp
    with open(f"timestamp-{group}.txt", "w") as f:
        f.write(time)

    download_objekts(group, id, front)

# 37564 000000000000000 000
# 26001 000000000000000 000
# 40 000000000000000000
# 5  000000000000000000
