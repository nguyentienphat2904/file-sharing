import time
import os
from dotenv import load_dotenv
from helper import main as helper
from prettytable import PrettyTable

load_dotenv()
BASE_URL = str(os.getenv('BASE_URL'))

def discover():
    response = helper.discover_peers(BASE_URL)
    if response and response.status_code == 200:
        peers = response.json().get('data', [])
        print("Discovered peers:")
        for peer in peers:
            print(f"IP: {peer['address']}, Port: {peer['port']}")
    else:
        print("Failed to discover peers.")

def create(username, password, ip, port):
    response = helper.create_peer(BASE_URL, username, password, ip, port)
    if response and response.status_code == 200:
        print(f"New peer created at IP: {ip}, Port: {port}")
    else:
        print("Failed to create peer.")

def ping(username, password, ip, port):
    response = helper.ping_peer(BASE_URL, username, password, ip, port)
    if response and response.status_code == 200:
        print(f"Ping to {ip}:{port} was successful.")
    else:
        print(f"Ping to {ip}:{port} failed.")

def fetch(hash_info):
    response = helper.fetch_all_file(BASE_URL)
    if response and response.status_code == 200 and response.json() and response.json()['data']:
        table = PrettyTable()
        table.field_names = ["Info Hash", "Name", "Size (bytes)", "Peers",]

        if(hash_info):
            data = response.json()['data'][0]
            peers = data.get('peers', [])
            peers_str = ', '.join([f"{peer['address']}:{peer['port']}" for peer in peers])

            if(peers):
                table.add_row([
                    data.get('hash_info'), 
                    data.get('name'), 
                    data.get('size'), 
                    peers_str
                ])
            else:
                table.add_row([
                    data.get('hash_info'), 
                    data.get('name'), 
                    data.get('size'), 
                    "No peers"
                ])
        else:
            for item in response.json()['data']:
                peer = item.get('peer', [])
                
                if peer:
                    table.add_row([
                        item.get('hash_info'), 
                        item.get('name'), 
                        item.get('size'), 
                        f"{peer.get('address')}:{peer.get('port')}"
                    ])
                else:
                    table.add_row([
                        item.get('hash_info'), 
                        item.get('name'), 
                        item.get('size'), 
                        "No peers"
                    ])

        print(table)

def process_input(cmd):
    params = cmd.split()
    
    if len(params) == 0:
        return
    try:
        if (params[0] == 'discover'):
            discover()
        elif (params[0] == 'create'):
            if len(params) == 1:
                print('')
            elif len(params) == 2:
                print('')
            elif len(params) > 5:
                print('Invalid command.')
            else:
                create(params[1], params[2], params[3], params[4])
        elif (params[0] == 'ping'):
            if len(params) == 5:
                ping(params[1], params[2], params[3], params[4])
            else:
                print('Invalid command.')
        elif (params[0] == 'fetch'):
            if len(params) == 1:
                fetch('')
            elif len(params) == 2:
                fetch(params[1])
            else:
                print('Invalid command')
    except IndexError as e:
        print('Invalid command')


if __name__ == "__main__":
    try:
        time.sleep(1)
        while True:
            cmd = input('>>')
            if cmd == 'exit':
                break

            process_input(cmd)

    except KeyboardInterrupt:
        print('\nMessenger stopped by user')
    finally:
        print("Cleanup done.")