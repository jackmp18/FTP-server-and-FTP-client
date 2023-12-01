import socket
import os

def recvAll(sock, numBytes):
    # The buffer to all data received from the client.
    recvBuff = b""
    
    # Keep receiving till all is received
    while len(recvBuff) < numBytes:
        
        # Attempt to receive bytes
        tmpBuff = sock.recv(numBytes - len(recvBuff))
        
        # The other side has closed the socket
        if not tmpBuff:
            break
        
        # Add the received bytes to the buffer
        recvBuff += tmpBuff
    
    return recvBuff

# Server address
serverAddr = "localhost"

# Server port
serverPort = 1234

# Create a TCP socket for the control connection
controlSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
controlSock.connect((serverAddr, serverPort))

# Wait for user input and handle commands
while True:
    command = input("ftp> ")
    cmd_parts = command.split()
    if cmd_parts[0] == "put" and len(cmd_parts) > 1:
        fileName = cmd_parts[1]
        if os.path.isfile(fileName):
            # Send the put command to the server
            controlSock.send(command.encode())

            # Receive the ephemeral port number
            ephemeral_port = int(controlSock.recv(1024).decode())

            # Create a new socket for the data connection
            dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSock.connect((serverAddr, ephemeral_port))

            # Open the file
            with open(fileName, "rb") as fileObj:
                # Read the entire file at once
                fileData = fileObj.read()

            # Get the size of the data read and convert it to string
            dataSizeStr = str(len(fileData))
            # Prepend 0's to the size string until the size is 10 bytes
            while len(dataSizeStr) < 10:
                dataSizeStr = "0" + dataSizeStr

            # Prepend the size of the data to the file data
            fileData = dataSizeStr.encode() + fileData

            # Send the file data over the data connection
            dataSock.sendall(fileData)
            print(f"Sent {len(fileData)} bytes over the data connection.")

            # Close the data connection
            dataSock.close()
        else:
            print("File not found.")
            
    elif cmd_parts[0].lower() == "ls":
        # Send the ls command to the server
        controlSock.send(command.encode())

        # Receive the ephemeral port number
        ephemeral_port = int(controlSock.recv(1024).decode())

        # Create a new socket for the data connection
        dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dataSock.connect((serverAddr, ephemeral_port))

        # Receive the list of files
        files_list = recvAll(dataSock, 4096)  # Adjust buffer size as needed
        print("Files on the server:\n", files_list.decode())

        # Close the data connection
        dataSock.close()
        
    elif cmd_parts[0].lower() == "get" and len(cmd_parts) > 1:
        # Send the get command to the server
        controlSock.send(command.encode())

        # Receive the ephemeral port number or file not found message
        serverResponse = controlSock.recv(1024).decode()

        if serverResponse.isdigit():
            ephemeral_port = int(serverResponse)

            # Create a new socket for the data connection
            dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dataSock.connect((serverAddr, ephemeral_port))

            # Receive the file size
            fileSizeBuff = recvAll(dataSock, 10)
            fileSize = int(fileSizeBuff)

            print(f"Receiving file of size {fileSize} bytes")

            # Receive the file data
            fileData = recvAll(dataSock, fileSize)

            # Save the file data to a file
            with open(cmd_parts[1], 'wb') as file:
                file.write(fileData)

            print(f"Received and saved file as {cmd_parts[1]}")

            # Close the data connection
            dataSock.close()
        else:
            print(serverResponse)  # Print the file not found message or any other message
    elif cmd_parts[0] == "exit":
        controlSock.send(command.encode())
        break
    else:
        print("Unknown command.")

# Close the control socket
controlSock.close()
