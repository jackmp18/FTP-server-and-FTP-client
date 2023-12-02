import socket
import os
import sys

# The port on which to listen
if len(sys.argv) != 2:
    print("Usage: python server.py <portnumber>")
    sys.exit(1)

try:
    listenPort = int(sys.argv[1])
except ValueError:
    print("Please input a port number.")
    sys.exit(1)

# Ensure the provided port number is within the valid range of 0-65535
if listenPort not in range(0, 65536):
    print("Port number must be in the range 0-65535.")
    sys.exit(1)

# Create a welcome socket.
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

# Start listening on the socket
welcomeSock.listen(1)

print("Server listening on port {}...".format(listenPort))

def recvAll(sock, numBytes):
    # The buffer to all data received from the client.
    recvBuff = b""
    
    # Keep receiving till all is received
    while len(recvBuff) < numBytes:
        
        # Attempt to receive bytes
        tmpBuff = sock.recv(numBytes)
        
        # The other side has closed the socket
        if not tmpBuff:
            break
        
        # Add the received bytes to the buffer
        recvBuff += tmpBuff
    
    return recvBuff

# Accept connections forever
while True:
    
    print("Waiting for connections...")
    
    # Accept connections
    clientSock, addr = welcomeSock.accept()
    
    print("Accepted connection from client: ", addr)
    
    # Process commands from the client
    while True:
        # Get the command from the client
        command = clientSock.recv(1024).decode()
        if not command or command == "exit":
            break  
        
        split_command = command.split()
        
        if split_command[0] == "put" and len(split_command) == 2:
            # Generate an ephemeral port for data transfer
            dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSock.bind(('', 0)) # Bind to any available port
            dataSock.listen(1)
            
            # Tell the client which port to connect to for data transfer
            ephemeral_port = dataSock.getsockname()[1]
            clientSock.send(str(ephemeral_port).encode())
            
            # Accept the connection from the client on the ephemeral port
            dataConn, _ = dataSock.accept()
            
            # Receive the size of the file from the client
            fileSizeBuff = recvAll(dataConn, 10)
            fileSize = int(fileSizeBuff)
            
            print("The file size is {} bytes".format(fileSize))
            
            # Receive the file data from the client
            fileData = recvAll(dataConn, fileSize)
            
            # Save the file data using the name provided by the client
            with open(split_command[1], 'wb') as file:
                file.write(fileData)
            
            print(f"The file data is: {split_command[1]}")
            
            # Close the data connection
            dataConn.close()
            dataSock.close()

        elif split_command[0] == "ls":
            # Generate an ephemeral port for data transfer
            dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSock.bind(('', 0))  # Bind to any available port
            dataSock.listen(1)

            # Tell the client which port to connect to for data transfer
            ephemeral_port = dataSock.getsockname()[1]
            clientSock.send(str(ephemeral_port).encode())

            # Accept the connection from the client on the ephemeral port
            dataConn, _ = dataSock.accept()

            # Get list of file names in the current directory
            files = os.listdir('.')
            files_list = '\n'.join(files).encode()

            # Send the list of files to the client
            dataConn.sendall(files_list)

            print("Sent list of files.")

            # Close the data connection
            dataConn.close()
            dataSock.close()
        
        elif split_command[0] == "get" and len(split_command) == 2:
            # Check if the requested file exists
            if os.path.isfile(split_command[1]):
                # Generate an ephemeral port for data transfer
                dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                dataSock.bind(('', 0))  # Bind to any available port
                dataSock.listen(1)

                # Tell the client which port to connect to for data transfer
                ephemeral_port = dataSock.getsockname()[1]
                clientSock.send(str(ephemeral_port).encode())

                # Accept the connection from the client on the ephemeral port
                dataConn, _ = dataSock.accept()

                # Open and read the file
                with open(split_command[1], 'rb') as file:
                    fileData = file.read()

                # Get the size of the data read and convert it to string
                dataSizeStr = str(len(fileData))
                # Prepend 0's to the size string until the size is 10 bytes
                while len(dataSizeStr) < 10:
                    dataSizeStr = "0" + dataSizeStr
                
                # Prepend the size of the data to the file data
                fileData = dataSizeStr.encode() + fileData

                # Send the file data over the data connection
                dataConn.sendall(fileData)

                print(f"Sent {split_command[1]} to the client.")

                # Close the data connection
                dataConn.close()
                dataSock.close()
            else:
                # Send a message indicating the file does not exist
                clientSock.send(b"File not found")

    
    # Close the control connection after the loop is exited
    clientSock.close()
