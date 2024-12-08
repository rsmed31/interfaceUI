import requests

BASE_URL = "http://localhost:8000"


def set_base_url(url):
    global BASE_URL
    if not url.startswith('http://') and not url.startswith('https://'):
        BASE_URL = f"http://{url}"
    else:
        BASE_URL = url

def fetch_health_status():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            return "Reachable"
        return "Not Reachable"
    except:
        return "Not Reachable"

def fetch_cpu_data():
    try:
        response = requests.get(f"{BASE_URL}/metrics/v1/cpu/usage")
        if response.status_code == 200:
            return response.json()
    except:
        return []

def fetch_cpu_core_info():
    try:
        response = requests.get(f"{BASE_URL}/metrics/v1/cpu/core")
        if response.status_code == 200:
            return response.json()
    except:
        return {}

def fetch_ram_data():
    try:
        response = requests.get(f"{BASE_URL}/metrics/v1/ram/usage")
        if response.status_code == 200:
            return response.json()
    except:
        return {}

def fetch_disk_data():
    try:
        response = requests.get(f"{BASE_URL}/metrics/v1/disk/usage")
        if response.status_code == 200:
            return response.json()
    except:
        return {}