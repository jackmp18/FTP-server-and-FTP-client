from socket import socket, AF_INET, SOCK_STREAM
from helpers import send_command

class DataConnection:
    def __init__(self, client_socket, data=None, timeout=60):
        """
        Initializes a DataConnection instance for managing ephemeral ports.

        Args:
            client_socket (socket): The main client socket.
            data (optional): Additional data associated with the connection.
            timeout (int, optional): Timeout value for the ephemeral socket.
        """
        self.client_socket = client_socket
        self.timeout = timeout
        self.data = data

        self._setup_ephemeral_socket()

    def _setup_ephemeral_socket(self):
        """
        Sets up an ephemeral socket for the instance.

        This method is intended to be called only by the class.
        """
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        self.socket.bind(('', 0))
        self.socket.listen(1)

    def get_port_number(self):
        """
        Returns the port number of the ephemeral socket.

        Returns:
            int: Port number of the ephemeral socket.
        """
        return self.socket.getsockname()[1]

    def wait_client(self):
        """
        Waits for a client connection on the ephemeral socket.

        Sends the port number to the main client socket.
        """
        print(f"Waiting for client on {self.get_port_number()}")
        send_command(self.client_socket, 2, self.get_port_number().to_bytes(2, byteorder="big"))
        (client_socket, addr) = self.socket.accept()
        self.client_socket = client_socket
