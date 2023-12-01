#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_STREAM
from subprocess import PIPE
import subprocess
import sys
import threading
import os

from dataConnection import DataConnection
from helpers import send_command

START = 0x01  # Start of message byte

def parse_message(buffer, client_socket):
    """
    Parses and handles commands received from the client.

    Args:
        buffer (list): List containing the bytes of the received message.
        client_socket (socket): The socket connected to the client.
    """
    print(buffer)
    if buffer[1] == b'\x05':
        # List files command
        conn = DataConnection(client_socket, timeout=3)
        try:
            conn.wait_client()
        except:
            print("Client didn't connect - aborting transfer.")
            return
        conn.client_socket.send(str.encode(f"\x01{subprocess.run(['ls', '-l', './files'], stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout}\x00"))
        print("Sent `ls` to client")

    elif buffer[1] == b'\x04':
        # Upload file command
        file_name = (b''.join(buffer[2:-1])).decode('utf-8')
        print(f"Client wants to upload {file_name}")

        # Setup ephemeral port
        conn = DataConnection(client_socket, timeout=3)
        try:
            conn.wait_client()
        except:
            print("Client didn't connect - aborting transfer.")
            return

        print("Client connected, receiving file...")
        file_size = 0
        with open(os.path.join('files', file_name), 'wb') as f:
            while True:
                data_in = conn.client_socket.recv(1)
                if data_in:
                    file_size += 1
                    f.write(data_in)
                else:
                    break

            f.close()

        print(f"Received {file_size} bytes from client")

    # Get command
    elif buffer[1] == b'\x03':
        file_name = (b''.join(buffer[2:-1])).decode('utf-8')

        # TODO: Remove this
        print(f"Client wants to get {file_name}")

        # Setup ephemeral port
        conn = DataConnection(client_socket, timeout=3)
        try:
            conn.wait_client()
        except:
            print("Client didn't connect - aborting transfer.")
            return

        # Check that the file exists
        if not os.path.exists(os.path.join('files', file_name)):
            print(f"{file_name} does not exist. File must be in the same directory as {__file__}")
            return

        print("Client connected, transferring file...")

        # Transfer file
        with open(os.path.join('files', file_name), 'rb') as f:
            conn.client_socket.sendall(f.read())

        print(f"Transferred {file_name} to client - {os.path.getsize(os.path.join('files', file_name))} bytes")

    # Exit command
    elif buffer[1] == b'\x02':
        print("Client is leaving")

    # Invalid buffer
    else:
        print("Invalid buffer -- error retrieving command from client")


def client_handler(client_socket, client_address):
    """
    Handles communication with a connected client.

    Args:
        client_socket (socket): The socket connected to the client.
        client_address (tuple): Tuple containing client's address information.
    """
    print(f"Client connected from {client_address}")

    command_buffer = []
    while 1:
        new_byte = client_socket.recv(1)
        command_buffer.append(new_byte)
        if new_byte == b"\x01":
            # Got start of message, reset the buffer
            print("Byte came in")
            command_buffer = [new_byte]
        elif new_byte == b"\x00":
            # Got end of message, parse it
            threading.Thread(target=parse_message, args=(command_buffer, client_socket)).start()
            command_buffer = []


def main():
    if len(sys.argv) <= 1:
        print(f"{sys.argv[0]} [portNum]")
        return

    server_port = int(sys.argv[1])
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(5)

    print(f"Server started on port {server_port}")

    while 1:
        (client_socket, addr) = server_socket.accept()
        threading.Thread(target=client_handler, args=(client_socket, addr)).start()

if __name__ == '__main__':
    main()
