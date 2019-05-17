#!/usr/bin/env python3
from pexpect import pxssh
import getpass
import socket
import time
import sys
import json
import os

def setup_socket_client(socket_host, socket_port):
    socket_session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for i in range(5):
        try:
            socket_session.connect((socket_host, socket_port))
            return socket_session
        except Exception as e:
            print(e)
            print("Cannot connect to the socket server.")
            time.sleep(1)
    raise Exception("Cannot connect to the socket server. Quit.")

def list_2_json_binary(a_list):
    dict_data = {"action": a_list[0], "content": a_list[1]}
    return json.dumps(dict_data).encode()

def socket_request(socket_host, socket_port, binary_data): ## one connection allows only one request
    socket_session = setup_socket_client(socket_host, socket_port)
    socket_session.sendall(binary_data)
    response = socket_session.recv(1024).decode()
    if response=="\n": response = ""## actually is empty, I added this "\n"
    return response

def is_forbidden(command):
    forbidden_list = ["sz", "rz"]
    for item in forbidden_list:
        if command.startswith(item): return True
    return False

if __name__ == '__main__':
    socket_host = "127.0.0.1"
    socket_port = 65335

    arguments = " ".join(sys.argv[1:])
    if arguments.startswith("--start"):
        status = socket_request(socket_host, socket_port, list_2_json_binary(["status", ""]))
        if status!="Responding":
            password = getpass.getpass()
            response = socket_request(socket_host, socket_port, list_2_json_binary(["start", password]))
            print(response)
        else:
            print("SSH already connected.")
    elif arguments.startswith("--status"):
        response = socket_request(socket_host, socket_port, list_2_json_binary(["status", ""]))
        print(response)
    elif arguments.startswith("--stop"):
        response = socket_request(socket_host, socket_port, list_2_json_binary(["stop", ""]))
        print(response)
    elif arguments.startswith("--send"):
        command = arguments[7:]
        if is_forbidden(command):
            raise Exception("This command is not avaiable")
        cwd = os.getcwd()
        if cwd.startswith("/Volumes/hpcc"):
            command = "cd ~/"+"/".join(cwd.split("/")[3:])+" && "+command
        response = socket_request(socket_host, socket_port, list_2_json_binary(["exec", command]))
        print(response, end="")
    else:
        print("Invalid arguments.")
    