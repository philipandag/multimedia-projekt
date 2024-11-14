import socket
import wave

# Set up the server (receiver)
host = 'localhost'
port = 12345
buffer_size = 1024  # Receive in chunks

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Waiting for connection...")
client_socket, addr = server_socket.accept()
print(f"Connection established with {addr}")

# Create a .wav file to save received audio
output_file = "received_audio.wav"
frame_rate = 8000  # Standard for audio CDs
num_channels = 1  # Mono audio
sample_width = 2  # 16-bit audio

# Open the .wav file for writing
with wave.open(output_file, 'wb') as wf:
    wf.setnchannels(num_channels)
    wf.setsampwidth(sample_width)
    wf.setframerate(frame_rate)

    # Receive data in chunks and write it to the .wav file
    while True:
        data = client_socket.recv(buffer_size)
        if not data:
            break
        wf.writeframes(data)

# Close the socket
client_socket.close()
server_socket.close()
print(f"Audio saved to {output_file}")
