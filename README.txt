Alex Nguyen alexnguyen1994@csu.fullerton.edu
Serafina Yu serafyu@csu.fullerton.edu
Jack Page
Terry Ma tma17@csu.fullerton.edu

Programming language used: python3

To execute the programs:

1. Navigate to the server directory and invoke the server.py with: python3 server.py <port number> (choose any port number within range)
2. On a separate terminal, navigate to the client directory and invoke client.py with: python3 client.py <server address> <server port number>
For simplicity, the server address is hard coded as localhost, so the client would connect with: python3 client.py localhost <server port number you chose>

for example: 
python3 server.py 1234
python3 client.py localhost 1234


Once connected, you can test the following commands on the client terminal:

ls command: type 'ls' into the client terminal to receive a list of files in the server directory

get command: type 'get <file name>' in the client terminal to receive the file from the server's directory and store it in the client's directory. e.g. get test1.txt

put command: type 'put <file name>' in the client terminal to send a file from the client's directory to the server's directory. e.g. put filetosend.txt

quit command: type 'quit' in the client terminal to disconnect the client

note: Make sure client.py is in the client folder and server.py is in the server folder. When client uses get, it will receive the file from the server folder and place it in the client folder. When client uses put, it will take a file from its client folder and place it in the server folder. 