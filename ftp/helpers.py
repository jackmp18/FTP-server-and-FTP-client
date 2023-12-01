def send_command(socket, code, data=None):
    """
    Sends a command over the given socket.

    Args:
        socket (socket): The socket to send the command through.
        code (int): The command code.
        data (str or bytes, optional): Additional data to send with the command.
    """
    out = bytearray(b'\x01')
    out.append(code)
    if isinstance(data, str):
        out += bytearray(data, "utf-8")
    elif isinstance(data, bytes):
        out += data
    out += b'\x00'
    
    socket.send(out)

def message_reader(socket):
    """
    Reads and parses messages from the given socket.

    Args:
        socket (socket): The socket to read messages from.
    """
    buffer = []
    while True:
        new_byte = socket.recv(1)
        buffer.append(new_byte)
        if new_byte == b"\x01":
            # Start of message encountered, reset the buffer
            buffer = []
        elif new_byte == b"\x00":
            # End of message encountered, parse and print
            print(b''.join(buffer[0:-1]).decode('utf-8'))
            buffer = []
            return
