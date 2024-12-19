# https://github.com/rebecasouza/python-udp

import pyaudio
import socket
import wave
from threading import Thread
from defines import *

frames = []
SOCK_ADDR=("127.0.0.1", PORT)
OUT_FILE="recording-received.wav"
print("Czas ramki = ", CHUNK/RATE)

def udpStream(CHUNK):
    i = 0
    sock = socket.socket(socket.AF_INET, SOCK)
    sock.bind(SOCK_ADDR)
    if SOCK == socket.SOCK_DGRAM:
        while True:
            soundData, addr = sock.recvfrom(CHUNK*CHANNELS*2)
            frames.append(soundData)
            print("receiving audio..." + str(i))
            i += 1
            if i >= N_FRAMES:
                break
    sock.close()

def play(stream, CHUNK):
    i = 0

    with wave.open(OUT_FILE, 'w') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)

        while True:
            if len(frames) >= 1:
                while True:
                    try:
                        frame = frames.pop(0)
                        wf.writeframes(frame)
                        stream.write(frame, CHUNK)
                        print("playing audio..." + str(i))
                        i += 1
                    except:
                        break
            
        wf.close()



            

if __name__ == "__main__":

    Audio = pyaudio.PyAudio()

    stream = Audio.open(format=FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    output = True,
                    frames_per_buffer = CHUNK,
                    )

    udpThread  = Thread(target = udpStream, args=(CHUNK,))
    AudioThread  = Thread(target = play, args=(stream, CHUNK,))
    udpThread.start()
    AudioThread.start()
    print("1")
    udpThread.join(RECORD_LENGTH+2)
    AudioThread.join(RECORD_LENGTH+2)
    print("2")
    stream.close()
