import socket
import time

# python3 recv.py <PATH_TO_SEND_FROM>


# File to send
filename = sys.argv[1]

# Setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)
sock.connect(server_address)

# Open the file to read data
with open(filename, 'rb') as f:
    while chunk := f.read(1024):  # Read 1 KB at a time
        sock.sendall(chunk)  # Send the chunk
        time.sleep(0.02)  # Simulate real-time streaming by adding a delay

sock.close()
