import json
import pytest
import scraper

# Test Reading the JSON Files

def test_read_json_data():
    assert isinstance(scraper.read_json("./data/Study (1).boxdicom"), dict)

def test_open_files():
    assert isinstance(scraper.open_files(), list)

def test_open_files_is_all_dicts():
    assert all(isinstance(file, dict) for file in scraper.open_files())


# Test parsing the JSON files 
@pytest.fixture
def data():
    return scraper.read_json("./data/Study (1).boxdicom")

def test_get_all_fileVersionId(data):
    assert isinstance(scraper.get_all_fileVersionId(data), list)

def test_get_shared_name(data):
    assert scraper.get_shared_name(data) == "pi4rsya9zqphh9o7iejsrt650cl7y0hf"

# Test Building Request URL
@pytest.fixture
def key():
    return '73106283297'

@pytest.fixture
def shared_name():
    return 'pi4rsya9zqphh9o7iejsrt650cl7y0hf'

def test_build_url(key, shared_name):
    url = scraper.build_url(key, shared_name)
    assert url == f"https://cloud.app.box.com/representation/file_version_{key}/dicom.dcm?shared_name={shared_name}"

def test_build_urls(data):
    assert isinstance(scraper.build_urls(data), list)

def test_build_urls_data(data):
    assert all(isinstance(x, tuple) for x in scraper.build_urls(data))
