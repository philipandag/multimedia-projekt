import wave
import random
import socket

def receive_audio(host='localhost', port=12345, output_file="received_audio.wav"):
    # Set up the UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    
    # Open the output file to write the received audio
    with wave.open(output_file, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(44100)  # Standard sample rate

        print("Receiving audio...")

        while True:
            data, addr = sock.recvfrom(1024)  # Receive up to 1024 bytes at a time
            if data:
                # Simulate packet loss: drop random packets
                if random.random() > 0.1:  # 10% packet loss
                    wf.writeframes(data)
            
            # Terminate if no more data is received (could be an end-of-stream signal)
            if not data:
                break
    
    print(f"Audio saved to {output_file}")

# Start receiving
receive_audio()