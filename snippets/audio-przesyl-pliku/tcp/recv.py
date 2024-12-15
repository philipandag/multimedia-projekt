import socket
import sys

# python3 recv.py <PATH_TO_SAVE_TO>



# Setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 12345)
sock.bind(server_address)
sock.listen(1)

conn, addr = sock.accept()

# Receive and write to file
filename = sys.argv[1]
with open(filename, 'wb') as f:
    while True:
        data = conn.recv(1024)  # Receive 1 KB at a time
        if not data:
            break
        f.write(data)

conn.close()
sock.close()
print(f"File received and saved as {filename}")
