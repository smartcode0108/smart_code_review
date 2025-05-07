import os
import json
import time
import requests

def fetch_data(urls):
    data = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data.append(response.json())
        else:
            print(f"Failed to fetch {url}")
        time.sleep(1)  # simulate delay
    return data

def save_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(json.dumps(data))

def process_data(data):
    for record in data:
        if "name" in record:
            print(f"User: {record['name']}")
        else:
            print("Missing name")
