import requests
import pytest
import json
import glob
import re
import os
import threading

def read_json(filepath):
    """Generic function to read return a file in json format

    Args:
        filepath (bytestram): Any file type that can be parsed into valid JSON

    Returns:
        dict: Python Dictionary -- essentially JSON
    """
    with open(filepath, "r") as infile:
        return json.load(infile)

def open_files():
    """Open any files contained in the data folder

    Returns:
        list: A list of dict objects
    """
    filepath = "./data/*.boxdicom"
    return [read_json(file) for file in glob.glob(filepath)]

def get_all_fileVersionId(data):
    """Looks through the provided dictionary and returns the fileVersionId for each DICOM image described

    Args:
        data (dict): The dictionary object of the study

    Returns:
        list: All the fileVersionIds of the study
    """
    return [o['meta']['fileVersionId'] for s in data['study']['series'] for o in s['objects']]

def get_shared_name(data):
    """Get's the shared name value from the folderUrl in the metadata

    Args:
        data (dict): dictionary of object of the studies JSON

    Returns:
        str: The shared name value
    """
    folderUrl = data['study']['meta']['folderUrl']
    regex = re.compile(r'https://cloud.box.com/s/(.*)', re.I)
    shared_name = regex.search(folderUrl)
    return shared_name[1]

def get_study_uid(data):
    return data['study']['dicomMetadata']['StudyInstanceUID']

def build_url(key, shared_name):
    """Create the URl to be used to download the image

    Args:
        key (str): The fileVersionId
        shared_name (str): The name of the folder the images are containined within

    Returns:
        str: The URL to use to request the imaging
    """
    return f"https://cloud.app.box.com/representation/file_version_{key}/dicom.dcm?shared_name={shared_name}"

def build_urls(data):
    """Returns a list of all the URLS you need to download the full study

    Args:
        data (dict): The study's JSON data

    Returns:
        list: A list of URLS required to download the full study
    """
    shared_name = get_shared_name(data)
    keys = get_all_fileVersionId(data)
    urls = [(build_url(key, shared_name), key) for key in keys]
    return urls

def download_file(folder_name, url, key):
    print("Downloading: " + key + " with URL: " + url)
    # Make request
    r = requests.get(url)
    # Save data
    with open(f"./download_data/{folder_name}/{key}.dcm", 'wb') as f:
        f.write(r.content)

def download_files(urls, folder_name = "download_study"):
    # Create the folder path
    try:
        os.mkdir('./download_data/' + folder_name)
    except FileExistsError:
        # If it already exists notify user and kill function    
        print("A folder with that study uid already exists. It is likely that you have already downloaded this study")
        return 

    threads = []
    for url, key in urls:
        x = threading.Thread(target=download_file, args=(folder_name, url, key))
        threads.append(x)
        x.start()
    
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    files = open_files()
    for file in files:
        download_files(build_urls(file), get_study_uid(file))