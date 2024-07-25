import json
import requests
from PIL import Image
import glob
import os

############ REQUESTS ############ 

# correct typo for group querry
group = input("Which group?\n")
if group.lower() in ["3s", "3 s", "triples", "triple s"]:
    group = "tripleS"
else:
    group = group.lower()

with open(f"timestamp-{group}.txt", "r") as f:
    timestamp = f.read()
    print("Old timestamp : ", timestamp)

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

############ Traitements ############ 

def get_all_values_by_key(data, target_key, results=None):
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

# Load JSON data from file
data = objekts

# Get all values for the specified key
id = get_all_values_by_key(data, "id")
front = get_all_values_by_key(data, "front")
time = max(get_all_values_by_key(data, "timestamp"))

print("New timestamp : ", time)
print("# of objekts : " , len(id))

with open(f"timestamp-{group}.txt", "w") as f:
    f.write(time)

cnt = 0
for i in range(len(id)):
    
    ############ téléchargement ############ 

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
            print(cnt)
    else:
        print(f"Failed to retrieve file. Status code: {response.status_code}")