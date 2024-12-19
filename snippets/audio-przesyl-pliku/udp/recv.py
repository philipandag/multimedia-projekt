import socket

# Setup UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 12345)
sock.bind(server_address)

# Receive and write to file
filename = 'received_output_udp.wav'
with open(filename, 'wb') as f:
    while True:
        data, address = sock.recvfrom(1024)  # Receive 1 KB at a time
        if not data:
            break
        f.write(data)

sock.close()
print(f"File received and saved as {filename}")
