import requests
import hashlib

def fetch_all_file(base_url):
    response = requests.get(f'{base_url}/api/files/fetch')
    return response

def publish_file(server_urls, file_name, file_size, file_hash_info, address, port):
    for server_url in server_urls:
            try:
                print(file_name, file_size, file_hash_info, address, port)
                response = requests.post(f'{server_url}/api/files/publish', json = {
                    'name': file_name,
                    'size': file_size,
                    'hash_info': file_hash_info,
                    'peer': {
                        'address': address,
                        'port': port
                    }
                })
                try:
                    json_response = response.json()
                    print(f"Response JSON: {json_response}")
                except ValueError:
                    print("Response is not in JSON format.")
            except Exception as e:
                print(f"An error occurred: {e}")

def initial_hash_info(file_path, hash_algorithm = 'sha1'):
    if hash_algorithm == 'sha1':
        hash_func = hashlib.sha1()
    elif hash_algorithm == 'sha256':
        hash_func = hashlib.sha256()
    else:
        raise ValueError("Unsupported hash algorithm. Use 'sha1' or 'sha256'.")
    
    with open(file_path, 'rb') as file:
        while chunk := file.read(4096):
            hash_func.update(chunk)

    return hash_func.hexdigest()

def fetch_file_by_hash_info(base_url, hash_info):
    try:
        return requests.get(f'{base_url}/api/fetch?hash_info={hash_info}')
    except:
        return None

def get_file_info_and_peers_keep_file(hash_info, tracker_urls):
    peers_keep_file = []
    file_name = None
    file_size = None
    
    for tracker_url in tracker_urls:
        response = fetch_file_by_hash_info(tracker_url, hash_info)
        if response and response.status_code == 200:
            data = response.json().get('data')
            file = data[0] if len(data) > 0 else None
            if file:
                if not file_name:
                    if 'name' in file:
                        file_name = file['name']
                if  not file_size:
                    if 'size' in file:
                        file_size = file['size']
                if 'peers' in file and len(file['peers']) > 0:
                    peers = [(peer['address'], peer['port']) for peer in file['peers']]
                    peers_keep_file.extend(peers)
    
    return file_name, file_size, set(peers_keep_file)

def announce_downloaded(base_url, file_hash_info, file_name, file_size, peer_id):
    return requests.post(f'{base_url}/api/files/publish', {
        'name': file_name,
        'size': file_size,
        'hash_info': file_hash_info,
        'peer_id': peer_id,
    })