import socket
import time

# File to send
filename = input("Enter filename")

# Setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)

# Open the file to read data
with open(filename, 'rb') as f:
    while chunk := f.read(1024):  # Read 1 KB at a time
        sock.sendto(chunk, server_address)  # Send the chunk
        time.sleep(0.02)  # Simulate real-time streaming by adding a delay

sock.close()
