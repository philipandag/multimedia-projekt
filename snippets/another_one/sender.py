import socket
import wave

def stream_audio(input_file="input_audio.wav", host='localhost', port=12345):
    with wave.open(input_file, 'rb') as wf:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        print(f"Streaming {input_file} to {host}:{port}")
        
        chunk_size = 1024
        while True:
            data = wf.readframes(chunk_size)
            if not data:
                break
            
            sock.sendto(data, (host, port))
        
        sock.close()
        print("Streaming complete.")

stream_audio()
