import socket
import threading

from concurrent.futures import ThreadPoolExecutor
import traceback
from helper import main as helper
import json
import os
import time
from dotenv import load_dotenv
import math
from queue import Queue
import random
from prettytable import PrettyTable

HOST = '127.0.0.1'
PORT = 65433

load_dotenv()
PIECE_SIZE = int(os.getenv('PIECE_SIZE', '512'))

def start_peer_server(peer_ip=HOST, peer_port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((peer_ip, peer_port))
        server_socket.listen()
        print(f"Peer is listening at {peer_ip}:{peer_port}")
        print("Please type your command:\n")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Connected to {client_address}")
                handle_request(client_socket)
            except Exception as e:
                print(f"An error occurred while accepting connections: {e}")

def handle_request(client_socket):
    with client_socket:
        data = client_socket.recv(1024).decode('utf-8')
        request = json.loads(data)

        if request['type'] == 'GET_FILE_STATUS':
            hash_info = request['hash_info']

            response = {
                'type': 'FILE_STATUS',
                'hash_info': hash_info,
                'pieces_status': []
            }

            with open('file_status.json', 'r') as f:
                data = json.load(f)

            if not hash_info in data or not data[hash_info]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"store/{data[hash_info]['name']}"
            
            response = {
                'type': 'FILE_STATUS',
                'hash_info': hash_info,
                'pieces_status': data[hash_info]['piece_status']
            }

            client_socket.sendall(json.dumps(response).encode('utf-8'))

        elif request['type'] == 'GET_FILE_CHUNK':
            hash_info = request['hash_info']
            chunk_list = request['chunk_list']
            chunk_data = []

            response = {
                'type': 'FILE_CHUNK',
                'hash_info': hash_info,
                'chunk_data': chunk_data
            }

            with open('file_status.json', 'r') as f:
                data = json.load(f)

            if not data[hash_info]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"store/{data[hash_info]['name']}"
            
            try:
                with open(file_name, "rb") as f:
                    for chunk_index in chunk_list:
                        f.seek(chunk_index * PIECE_SIZE)
                        data = f.read(PIECE_SIZE)
                        chunk_data.append(data.decode('latin1'))
            except FileNotFoundError:
                print(f"File {file_name} does not exit.")
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            
            response['chunk_data'] = chunk_data

            client_socket.sendall(json.dumps(response).encode('utf-8'))
        elif request['type'] == 'PING':
            response = {
                'type': 'PONG'
            }
            client_socket.sendall(json.dumps(response).encode('utf-8'))

def connect_to_peer_and_get_file_status(peer_ip, peer_port, hash_info):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting...")
            s.connect((peer_ip, int(peer_port)))
            # print(f"Connected to {peer_ip}:{peer_port}")
            
            request = {
                'type': 'GET_FILE_STATUS',
                'hash_info': hash_info
            }

            s.sendall(json.dumps(request).encode('utf-8'))
            
            response_data = s.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            if response['type'] == 'FILE_STATUS' and response['hash_info'] == hash_info:
                pieces_status = response['pieces_status']
                return peer_ip, peer_port, pieces_status
            else:
                return None, None, None
    except (socket.error, ConnectionRefusedError, TimeoutError) as e:
        print(f"Connection error: {e}")
        return None, None, None

def connect_to_peer_and_download_file_chunk(peer_ip, peer_port, hash_info, chunk_list, file_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((peer_ip, int(peer_port)))
        print(f"Connected to {peer_ip}:{peer_port}")
        
        request = {
            'type': 'GET_FILE_CHUNK',
            'hash_info': hash_info,
            'chunk_list': chunk_list
        }

        s.sendall(json.dumps(request).encode('utf-8'))
        
        response_data = s.recv(4096)
        response = json.loads(response_data.decode('utf-8'))
        if response['type'] == 'FILE_CHUNK' and response['hash_info'] == hash_info:
            chunk_data = response['chunk_data']
            
            with open(file_path, "r+b") as f:  
                for i, chunk in enumerate(chunk_data):
                    f.seek(chunk_list[i] * PIECE_SIZE)
                    f.write(chunk.encode('latin1'))
                    print(f"Chunk {chunk_list[i]} has been written into file")
        else:
            print("Has been received invalid response from peer")


def download(hash_info, tracker_urls):
    file_name, file_size, peers_keep_file = helper.get_file_info_and_peers_keep_file(hash_info, tracker_urls)

    file_path = f"store/{file_name}"

    num_of_pieces = math.ceil(file_size / int(PIECE_SIZE))

    if not os.path.exists(file_path):
        with open(file_path, "wb") as f:
            pass

    peers_file_status = {}
    chunk_count = {}

    piece_status_lock = threading.Lock()
    chunk_count_lock = threading.Lock()
    piece_download_lock = threading.Lock()
    file_status_lock = threading.Lock()

    connection_queue = Queue()

    for address, port in peers_keep_file:
        if address != HOST or port != PORT:
            connection_queue.put((address, port))

    def get_file_status():
        while not connection_queue.empty():
            ip, port = connection_queue.get()
            try:
                peer_ip, peer_port, pieces_status = connect_to_peer_and_get_file_status(ip, port, hash_info)
                if peer_ip and peer_port and pieces_status and len(pieces_status) > 0:
                    if len(pieces_status) != num_of_pieces:
                        continue
                    
                    with piece_status_lock:
                        peers_file_status[(peer_ip, peer_port)] = pieces_status

                    with chunk_count_lock:
                        for chunk_index, has_chunk in enumerate(pieces_status):
                            if has_chunk:
                                if chunk_index not in chunk_count:
                                    chunk_count[chunk_index] = 0
                                chunk_count[chunk_index] += 1
            except:
                print(f"Error connecting to {ip}:{port}")
            connection_queue.task_done()

    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(5):
            executor.submit(get_file_status)

    connection_queue.join()

    chunk_peers_map = {}
    for chunk_index in range(num_of_pieces):
        peers_with_chunk = [(peer, sum(status)) for peer, status in peers_file_status.items() if status[chunk_index]]
        if len(peers_with_chunk) > 0:
            chunk_peers_map[chunk_index] = peers_with_chunk
            random.shuffle(chunk_peers_map[chunk_index])

    chunk_queue = Queue()
    for chunk_index in chunk_peers_map.keys():
        chunk_queue.put(chunk_index)

    piece_has_been_downloaded = [0 for _ in range(num_of_pieces)]

    def download_chunk():
        while not chunk_queue.empty():
            chunk_index = chunk_queue.get()
            peers = chunk_peers_map.get(chunk_index, [])

            for (ip, port), _ in peers:
                with piece_download_lock:
                    if piece_has_been_downloaded[chunk_index] == 1:
                        continue
                
                try:
                    connect_to_peer_and_download_file_chunk(ip, port, hash_info, [chunk_index], file_path)

                    with piece_download_lock:
                        piece_has_been_downloaded[chunk_index] = 1
                    break
                except Exception as e:
                    print(f"Error downloading chunk {chunk_index} from {ip}:{port}: {e}")

            chunk_queue.task_done()

    with ThreadPoolExecutor(max_workers=5) as executor:
        for _ in range(5):
            executor.submit(download_chunk)

    chunk_queue.join()

    def update_file_status():
        with file_status_lock:
            try:
                with open('file_status.json', 'r') as f:
                    file_status_data = json.load(f)
                    if not file_status_data.get(hash_info):
                        file_status_data[hash_info] = {
                            'name': file_name,
                            'piece_status': piece_has_been_downloaded
                        }
                    else:
                        file_status_data[hash_info]['piece_status'] = piece_has_been_downloaded

                with open('file_status.json', 'w') as json_file:
                    json.dump(file_status_data, json_file, indent=4)
            except FileNotFoundError:
                print('File file_status.json does not exist')

    update_file_status()

    helper.publish_file(tracker_urls, file_name, file_size, hash_info, address=HOST, port=PORT)
    print('Download and announce server successfully')


def fetch_file(server_url, hash_info):
    response = None
    if hash_info:
        response = helper.fetch_file_by_hash_info(server_url, hash_info)
    else:
        response = helper.fetch_all_file(server_url)

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
        
def publish(file_path, tracker_urls):
    if not os.path.exists(file_path):
        print(f'Path {file_path} does not exist')
        return

    if not os.path.isfile(file_path):
        print(f'{file_path} is not a file')
        return
    
    hash_info = helper.initial_hash_info(file_path)
    helper.publish_file(tracker_urls, os.path.basename(file_path), int(os.path.getsize(file_path)), hash_info, HOST, PORT)

    print('Publish file successfully')

def process_input(cmd):
    params = cmd.split()

    if len(params) == 0:
        return
    try:
        if params[0] == 'download':
            if len(params) == 1:
                print('Argument hash_info is required')
            if len(params) == 2:
                print('Tracker urls must be specified')
            download(params[1], params[2:])
        elif params[0] == 'fetch':
            if len(params) == 1:
                print('Argument server url is required')
            elif len(params) == 2:
                fetch_file(params[1], None)
            elif len(params) == 3:
                fetch_file(params[1], params[2])
            else:
                raise
        elif params[0] == 'publish':
            if len(params) == 1:
                print('Argument file path is required')
                return
            elif len(params) == 2:
                print('Tracker urls must be specified')
                return
            publish(params[1], params[2:])
        
        else:
            print('Invalid command')
    except IndexError as e:
        print('Invalid command')

if __name__ == "__main__":
    try:
        server_thread = threading.Thread(target=start_peer_server, args=(HOST, PORT))
        server_thread.start()

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
        