#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_STREAM
from helpers import send_command, message_reader
import sys
import os

START = 0x01
END = 0x00

def get_port_number(data):
    """
    Extracts the port number from a 0x05 packet in the data argument.
    Returns an integer with the port number encoded via the 2 data bytes in the packet.
    """
    return int.from_bytes(data[2:4], byteorder="big")

def handle_ls(client_socket, client_host):
    """
    Handles the 'ls' command, sending it to the server and displaying the server's response.
    """
    send_command(client_socket, 5)
    eph_port_number = get_port_number(client_socket.recv(5))

    print(f"Connecting to socket at {client_host}:{eph_port_number}")

    eph_socket = socket(AF_INET, SOCK_STREAM)
    eph_socket.connect((client_host, eph_port_number))

    message_reader(eph_socket)

    eph_socket.close()

def handle_put(client_socket, client_host, file_name):
    """
    Handles the 'put' command, sending a file to the server.
    """
    if not os.path.exists(file_name):
        print(f"{file_name} does not exist. File must be in the same directory as {__file__}\n")
        return

    send_command(client_socket, 4, file_name)
    eph_port_number = get_port_number(client_socket.recv(5))

    print(f"Attempting to connect to socket at {client_host}:{eph_port_number}")

    eph_socket = socket(AF_INET, SOCK_STREAM)
    eph_socket.connect((client_host, eph_port_number))

    print(f"Connected, transferring {file_name}")

    with open(file_name, 'rb') as f:
        eph_socket.sendall(f.read())

    eph_socket.close()

    print(f"Transfer complete. {os.path.getsize(file_name)} bytes trasnferred.\n")

def handle_get(client_socket, client_host, file_name):
    """
    Handles the 'get' command, receiving a file from the server.
    """
    send_command(client_socket, 3, file_name)
    eph_port_number = get_port_number(client_socket.recv(5))

    print(f"Attempting to connect to socket at {client_host}:{eph_port_number}")

    eph_socket = socket(AF_INET, SOCK_STREAM)
    eph_socket.connect((client_host, eph_port_number))

    print(f"Connected, transferring {file_name}")

    file_size = 0

    data_in = eph_socket.recv(1)
    if data_in == b"":
        print(f"No data returned. File does not exist at the server\n")
    else:
        with open(file_name, 'wb') as f:
            file_size += 1
            f.write(data_in)
            while True:
                data_in = eph_socket.recv(1)
                if data_in:
                    file_size += 1
                    f.write(data_in)
                else:
                    break
        f.close()
        print(f"Done! Transferred {file_size} bytes\n")

    eph_socket.close()

def main():
    """
    Main function to handle user input and execute corresponding commands.
    """
    client_host = sys.argv[1]
    client_port = int(sys.argv[2])

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((client_host, client_port))
    print(f"Connected to {client_host}:{client_port}")

    while True:
        argument = input(">> ").split()
        if argument:
            command = argument[0]
            if command == "ls":
                handle_ls(client_socket, client_host)
            elif command == "put":
                if len(argument) != 2:
                    print(f"ERROR - Please write commands in the format of: 'put <fileName>'\n")
                else:
                    handle_put(client_socket, client_host, argument[1])
            elif command == "get":
                if len(argument) != 2:
                    print(f"ERROR - Please write commands in the format of: 'get <fileName>'\n")
                else:
                    handle_get(client_socket, client_host, argument[1])
            elif command == "exit":
                if len(argument) != 1:
                    print(f"ERROR - exit command does not accept additional arguments\n")
                else:
                    send_command(client_socket, 2)
                    client_socket.close()
                    print(f"Exiting...")
                    sys.exit(0)
            else:
                print(f"ERROR - not a valid command. Enter one of the following commands: ls, get, put, exit\n")

if __name__ == '__main__':
    main()
