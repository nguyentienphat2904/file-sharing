import requests

def discover_peers(base_url):
    try:
        return requests.get(f"{base_url}/api/peers/discover")
    except:
        return None

def fetch_all_file(base_url):
    response = requests.get(f'{base_url}/api/files/fetch')
    return response

def fetch_file_by_hash_info(base_url, hash_info):
    try:
        return requests.get(f'{base_url}/api/files/fetch?hash_info={hash_info}')
    except:
        return None

def create_peer(base_url, username, password, ip, port):
    try:
        payload = {'username': username, 'password': password, 'address': ip, 'port': port}
        return requests.post(f"{base_url}/api/peers/create", json=payload)
    except:
        return None

def ping_peer(base_url, username, password, ip, port):
    try:
        payload = {'username': username, 'password': password, 'address': ip, 'port': port}
        return requests.get(f"{base_url}/api/peers/create", json=payload)
    except:
        return None