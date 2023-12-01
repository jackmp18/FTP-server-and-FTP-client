import socket
import os

# The port on which to listen
listenPort = 1234

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
        if not command or command.lower() == "exit":
            break  # Exit the loop and wait for a new connection
        
        cmd_parts = command.split()
        
        if cmd_parts[0] == "put" and len(cmd_parts) > 1:
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
            
            print("Receiving file of size {} bytes".format(fileSize))
            
            # Receive the file data from the client
            fileData = recvAll(dataConn, fileSize)
            
            # Save the file data using the name provided by the client
            with open(cmd_parts[1], 'wb') as file:
                file.write(fileData)
            
            print(f"Received file data and saved as {cmd_parts[1]}")
            
            # Close the data connection
            dataConn.close()
            dataSock.close()

        elif cmd_parts[0].lower() == "ls":
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
        
        elif cmd_parts[0].lower() == "get" and len(cmd_parts) > 1:
            # Check if the requested file exists
            if os.path.isfile(cmd_parts[1]):
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
                with open(cmd_parts[1], 'rb') as file:
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

                print(f"Sent {cmd_parts[1]} to the client.")

                # Close the data connection
                dataConn.close()
                dataSock.close()
            else:
                # Send a message indicating the file does not exist
                clientSock.send(b"File not found")

    
    # Close the control connection after the loop is exited
    clientSock.close()
