#!/usr/bin/env python3
from pexpect import pxssh
import getpass
import socket
import time
import json

def ssh_login_with_password(host, username, password):
    ssh = pxssh.pxssh()
    ssh.login(host, username, password)
    return ssh

def ssh_exec(ssh_session, command):
    lines = command.count("\n")
    ssh_session.sendline(command)
    ssh_session.prompt()
    response = "\n".join(ssh_session.before.decode().split("\n")[lines+1:])
    return response

def setup_socket_server(socket_host, socket_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket_host, socket_port))
    except Exception as e:
        #print("The port is in use, retry after 10 seconds...")
        raise Exception(e)
        time.sleep(10)
        s.bind((socket_host, socket_port))
    s.listen()
    return s

def parse_json_binary(json_data):
    try:
        dict_data = json.loads(json_data.decode())
        action = dict_data.get("action")
        content = dict_data.get("content")
        return action, content
    except:
        return "", ""
    

def ssh_login(host, username, socket_session):
    for i in range(10):
        print("wait for", i)
        conn, addr = socket_session.accept()
        action, content = parse_json_binary(conn.recv(1024))
        print("recevied", i, action)
        if action=="start":
            print("Connecting to server...")
            password = content
            try:
                ssh_session = ssh_login_with_password(host, username, password)
                conn.sendall("Connected.".encode())
                return ssh_session
            except Exception as e:
                conn.sendall(str(e).encode())
                print(e)
        elif action=="stop":
            conn.sendall("Stop listening.".encode())
            socket_session.close()
            print("Stop listening.")
            exit()
        elif action=="status":
            print("Status look up.")
            conn.sendall("NeedPassword".encode())
        elif action=="exec":
            print("exec without login.")
            conn.sendall("NeedPassword".encode())
        else:
            conn.sendall("Invalid action".encode())
            print("Invalid action")
    raise Exception("Wrong passwords or non-login action were provided too many times. Quit.")

def is_forbidden(command):
    forbidden_list = ["sz", "rz"]
    for item in forbidden_list:
        if command.startswith(item): return True
    return False

def start_responding(ssh_session, socket_session):
    while True:
        conn, addr = socket_session.accept()
        action, content = parse_json_binary(conn.recv(1024))
        if action=="stop":
            conn.sendall("Disconnected to SSH server".encode())
            socket_session.close()
            print("Disconnected to SSH server.")
            exit()
        elif action=="exec":
            command = content
            if is_forbidden(command):
                conn.sendall("Forbidden command.".encode())
            else:
                remote_stdout = ssh_exec(ssh_session, command)
                if not remote_stdout: remote_stdout = "\n" ## if empty, the response cannot be sent successfully
                conn.sendall(remote_stdout.encode())
        elif action=="status":
            conn.sendall("Responding".encode())
        else:
            conn.sendall("Invalid action".encode())
            print("Invalid action")


if __name__ == '__main__':
    socket_host = "127.0.0.1"
    socket_port = 65335
    socket_session = setup_socket_server(socket_host, socket_port)
    print("Socket server started.")

    ssh_host = "access.nju.edu.cn"
    username = "zhj_shimj"
    #password = getpass.getpass('password: ')
    ssh_session = ssh_login(ssh_host, username, socket_session)
    print("SSH connected.")
    print("Listening on port "+str(socket_port)+"...")
    start_responding(ssh_session, socket_session)

