import socket
import wave
import time

host = 'localhost'
port = 12345
buffer_size = 1024
chunk_duration = 0.04

bytes_per_sample = 2

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

input_file = "input_audio.wav"
with wave.open(input_file, 'rb') as wf:
    num_channels = wf.getnchannels()
    sample_width = wf.getsampwidth()
    frame_rate = wf.getframerate()
    
    samples_per_chunk = int(frame_rate * chunk_duration)
    chunk_size = samples_per_chunk * num_channels * sample_width

    while True:
        data = wf.readframes(samples_per_chunk)
        if not data:
            break

        client_socket.sendall(data)
        time.sleep(chunk_duration)


client_socket.close()
print(f"Audio from {input_file} sent in real-time to the server.")
