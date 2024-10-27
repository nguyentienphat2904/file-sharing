import socket
import threading

from concurrent.futures import ThreadPoolExecutor
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
PORT = 65321

load_dotenv()
PIECE_SIZE = int(os.getenv('PIECE_SIZE', '512'))

def start_peer_server(peer_ip=HOST, peer_port = PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((peer_ip, peer_port))
        server_socket.listen(5)
        print(f"Peer is listening at {peer_ip}:{peer_port}")
        print(f"Enter command:\n")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connect to {client_address}")
            handle_request(client_socket)

def handle_request(client_socket):
    with client_socket:
        data = client_socket.recv(1024).decoce('utf-8')
        request = json.loads(data)

        if (request['type']) == "GET_FILE_STATUS":
            hash_info = request['hash_info']

            response = {
                'type': 'FILE_STATUS',
                'hash_info': hash_info,
                'piece_status': []
            }

            with open('file_status.json', 'r') as fs:
                data = json.load(fs)

            if not data[hash_info]:
                client_socket.sendall(json.dumps(response).encode('utf-8'))
                return
            
            file_name = f"store/{data[hash_info]['name']}"

            response = {
                'type': 'FILE_STATUS',
                'hash_info': hash_info,
                'piece_status': data[hash_info]['piece_status']
            }

            client_socket.sendall(json.dumps(response).encode('utf-8'))
        elif request['type'] == "GET_FILE_CHUNK":
            hash_info = request['hash_info']
            chunk_list = request['chunk_list']
            chunk_data = []

            response = {
                'type': 'FILE_CHUNK',
                'hash_info': hash_info,
                'chunk_data': []
            }

            with open('file_status.json', 'r') as fs:
                data = json.load(fs)

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
            except:
                print(f"File {file_name} does not exist.")
                client_socket.sendall(json.dumps(response).encode('uft-8'))
                return
            
            response['chunk-data'] = chunk_data

            client_socket.sendall(json.dumps(response).encode('utf-8'))
        elif request['type'] == "PING":
            response = {
                'type': 'PONG'
            }
            client_socket.sendall(json.dumps(response).encode('utf-8'))

def connect_to_peer_and_get_file_status(peer_ip, peer_port, hash_info):
    return

def connect_to_peer_and_download_file_chunk(peer_ip, peer_port, info_hash, chunk_list, file_path):
    return

def download(info_hash, tracker_urls):
    return

def fetch_file(server_url, hash_info):
    return

def publish(file_path, tracker_urls):
    if not os.path.exists(file_path):
        print(f'Path {file_path} does not exist')
        return

    if not os.path.isfile(file_path):
        print(f'{file_path} is not a file')
        return
    
    hash_info = helper.initial_hash_info(file_path)
    helper.publish_file(tracker_urls, os.path.basename(file_path), os.path.getsize(file_path), hash_info, HOST, PORT)

    print('Publish file successfully')

def process_input(cmd):
    params = cmd.split()

    if len(params) == 0: return

    try:
        if params[0] == 'download':
            if len(params) == 1:
                print("Argument hash_info is required")
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
        else: print("Invalid command")

    except IndexError as e:
        print ('Invalid command')

if __name__ == "__main__":
    try:
        server_thread = threading.Thread(target=start_peer_server, args=(HOST, PORT))
        server_thread.start()

        time.sleep(1)
        while True:
            cmd = input('>>')
            if cmd == '^C':
                break

            process_input(cmd)

    except KeyboardInterrupt:
        print("\nMessage stop by user")
    finally:
        print("Cleanup done.")