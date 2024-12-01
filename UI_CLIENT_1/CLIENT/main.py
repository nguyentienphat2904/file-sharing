import socket
import threading

from concurrent.futures import ThreadPoolExecutor
import traceback
from client_helper import main as helper
import json
import os
import time
from dotenv import load_dotenv
import math
from queue import Queue
import random
from prettytable import PrettyTable
from urllib.parse import parse_qs, urlparse, urlencode


HOST = socket.gethostbyname(socket.gethostname())
# HOST = '127.0.0.1'
PORT = 65431

load_dotenv()
PIECE_SIZE = int(os.getenv('PIECE_SIZE', '512'))

stop_event = threading.Event()

def start_peer_server(peer_ip=HOST, peer_port=PORT):
    stop_flag = False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((peer_ip, peer_port))
        server_socket.listen()
        print(f"Peer is listening at {peer_ip}:{peer_port}")
        print("Please type your command:\n")

        while not stop_event.is_set():
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Connected to {client_address}")
                handle_request(client_socket)
            except Exception as e:
                print(f"An error occurred while accepting connections: {e}")

def stop_peer_server():
    stop_event.set()

def handle_request(client_socket):
    with client_socket:
        data = client_socket.recv(4096).decode('utf-8')
        request = json.loads(data)

        if request['type'] == 'GET_FILE_STATUS':
            hash_info = request['hash_info']

            response = {
                'type': 'FILE_STATUS',
                'hash_info': hash_info,
                'pieces_status': []
            }

            with open('CLIENT/file_status.json', 'r') as f:
                data = json.load(f)

            if not hash_info in data or not data[hash_info]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"CLIENT/store/{data[hash_info]['name']}"
            
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

            with open('CLIENT/file_status.json', 'r') as f:
                data = json.load(f)

            if not data[hash_info]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            file_name = f"CLIENT/store/{data[hash_info]['name']}"
            
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



class MagnetLink:
    def __init__(self, hash_info: str, name: str, tracker_url: str):
        self.hash_info = hash_info
        self.name = name
        self.tracker_url = tracker_url

    def to_magnet(self) -> str:    
        return f"magnet:?xt=urn:btih:{self.hash_info}&dn={self.name}&tr={self.tracker_url}"

    @classmethod
    def from_magnet(cls, magnet: str):
        if not magnet.startswith("magnet:?"):
            raise ValueError("Chuỗi không đúng định dạng magnet.")
        
        query = magnet[len("magnet:?"):]
        params = dict(param.split("=", 1) for param in query.split("&") if "=" in param)
        
        xt = params.get("xt", "")
        if xt.startswith("urn:btih:"):
            hash_info = xt[len("urn:btih:"):]
        else:
            hash_info = ""
        name = params.get("dn", "")
        tracker_url = params.get("tr", "")
        
        return cls(hash_info, name, tracker_url)
    
    def de_magnet(self) :
        return self.hash_info, self.name, self.tracker_url


def create_magnet(hash_info, name, tracker_url):
    magnetLink = MagnetLink(hash_info,name, tracker_url)
    return magnetLink.to_magnet()

        
def download_from_magnet(magnet) :    
    magnetLink = MagnetLink.from_magnet(magnet)
    hash_info, tmp, tracker_urls = magnetLink.de_magnet()
    print(magnetLink.de_magnet())
    # download(hash_info, tracker_urls)



def download(hash_info, tracker_urls):
    file_name, file_size, peers_keep_file = helper.get_file_info_and_peers_keep_file(hash_info, tracker_urls)

    file_path = f"CLIENT/store/{file_name}"

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
                with open('CLIENT/file_status.json', 'r') as f:
                    file_status_data = json.load(f)
                    if not file_status_data.get(hash_info):
                        file_status_data[hash_info] = {
                            'name': file_name,
                            'piece_status': piece_has_been_downloaded
                        }
                    else:
                        file_status_data[hash_info]['piece_status'] = piece_has_been_downloaded

                with open('CLIENT/file_status.json', 'w') as json_file:
                    json.dump(file_status_data, json_file, indent=4)
            except FileNotFoundError:
                print('File file_status.json does not exist')

    update_file_status()

    helper.publish_file(tracker_urls, file_name, file_size, hash_info, address=HOST, port=PORT)
    print('Download and announce server successfully')


def fetch():
    with open('CLIENT/file_status.json', 'r') as file:
        data = json.load(file)
    print(data)
    return data

def fetch_file(server_url, hash_info):
    response = None
    if hash_info:
        response = helper.fetch_file_by_hash_info(server_url, hash_info)
    else:
        response = helper.fetch_all_file(server_url)
    return response

        
def publish(file_path, tracker_urls):
    if not os.path.exists(file_path):
        print(f'Path {file_path} does not exist')
        return 1

    if not os.path.isfile(file_path):
        print(f'{file_path} is not a file')
        return 2
    
    hash_info = helper.initial_hash_info(file_path)
    # create file status
    num_of_pieces = math.ceil(int(os.path.getsize(file_path)) / int(PIECE_SIZE))
    file_name = os.path.basename(file_path).split('/')
    piece_status = [1 for _ in range(num_of_pieces)]
    file_path_status = 'CLIENT/file_status.json'

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump({}, f)

    
    with open(file_path_status, 'r') as f:
        file_status_data = json.load(f)
        if not file_status_data.get(hash_info):
            file_status_data[hash_info] = {
                'name': file_name[0],
                'piece_status': piece_status
            }
        else:
            file_status_data[hash_info]['piece_status'] = piece_status

    with open('CLIENT/file_status.json', 'w') as json_file:
        json.dump(file_status_data, json_file, indent=4)
        
    return helper.publish_file(tracker_urls, os.path.basename(file_path), int(os.path.getsize(file_path)), hash_info, HOST, PORT)

    


        