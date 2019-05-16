#!/usr/bin/env python3
from pexpect import pxssh
import getpass
import socket
import time

def ssh_login(host, username, password):
    ssh = pxssh.pxssh()
    ssh.login(host, username, password)
    return ssh

def ssh_retrieve(ssh_session, command):
    lines = command.count("\n")
    ssh_session.sendline(command)
    ssh_session.prompt()
    response = "\n".join(ssh_session.before.decode().split("\n")[lines+1:-1])
    return response

def setup_socket_server(socket_server, socket_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket_server, socket_port))
    except:
        print("The port is in use, retry after 5 seconds...")
        time.sleep(5)
        s.bind((socket_server, socket_port))
    s.listen()
    return s

def start_responding(ssh_session, socket_session):
    while True:
        conn, addr = socket_session.accept()
        command = conn.recv(1024).decode()
        if command=="logout":
            print("Disconnected.")
            exit()
        stdout = ssh_retrieve(ssh_session, command)
        conn.sendall(stdout.encode())


if __name__ == '__main__':
    # socket_server = "127.0.0.1"
    # socket_port = 65335
    # socket_session = setup_socket_server(socket_server, socket_port)
    # print("Socket server started.")

    ssh_host = "access.nju.edu.cn"
    username = "zhj_shimj"
    password = getpass.getpass('password: ')
    ssh_session = ssh_login(ssh_host, username, password)
    print("SSH connected.")
    # print("Listening on port "+str(socket_port)+"...")
    while True:
        command = input()
        response = ssh_retrieve(ssh_session, command)
        print(response)

    # start_responding(ssh_session, socket_session)