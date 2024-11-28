import requests

def resigter_peer(base_url, username, password, ip, port) :
    try:
        payload = {'username': username, 'password': password, 'address': ip, 'port': port}
        return requests.get(f"{base_url}/api/auth/register", json = payload)
    except:
        return None
    
def login_peer(bare_url, username, password) :
    try:
        payload = {'username': username, 'password': password}
        return requests.get(f"{bare_url}/api/auth/login", json=payload)
    except:
        return None

        
