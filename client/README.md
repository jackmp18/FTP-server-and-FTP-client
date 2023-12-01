Alex Nguyen
Serafina Yu
Jack Page
Timothy Bryant JR
Michael Martinez

To execute the programs:

1. Navigate to the server directory and invoke the server.py with: python server.py <port number>
2. On a separate terminal, navigate to the client directory and invoke client.py with: python client.py <server address> <server port number>

For simplicity, the server address is hard coded as localhost, so the client would connect with: python client.py localhost <server port number>

Once connected,

ls command: type 'ls' into the client terminal to receive a list of files in the server directory

get command: type 'get <file name>' in the client terminal to receive the file from the server's directory and store it in the client's directory

put command: type 'put <file name>' in the client terminal to send a file from the client's directory to the server's directory

exit command: type 'exit' in the client terminal to disconnect the client