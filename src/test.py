import json
import time
import requests


def fetch_data(urls):
    """
    ## Scraping Data from Multiple URLs
    
    Extracts data from multiple URLs and returns a list of JSON responses.
    
    Args:
        urls (list): List of URLs to scrape data from.
    
    Returns:
        list: List of JSON responses from successful requests.
    """
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
    """
    **Docstring:**
    
    
    Write the given data as a JSON file.
    
    Args:
        data (dict): The data to be written to the file.
    
    Returns:
        None
    """
    with open(filename, "w") as f:
        f.write(json.dumps(data))


def process_data(data):
    """
    **Docstring:**
    
    Summary:
    Prints the name of the user if it is present in the record dictionary.
    
    Args:
        record (dict): A dictionary containing user information.
    
    Returns:
        None
    """
    for record in data:
        if "name" in record:
            print(f"User: {record['name']}")
        else:
            print("Missing name")
