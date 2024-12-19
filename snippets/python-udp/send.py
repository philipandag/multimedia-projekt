import pyaudio
import socket
from threading import Thread
from defines import *
import wave
import struct
import sys
import time

frames = []
SOCK_ADDR=("127.0.0.1", PORT)
IN_FILE=sys.argv[1]

def udpStream():
    i = 0
    if SOCK == socket.SOCK_DGRAM:
        sock = socket.socket(socket.AF_INET, SOCK)
        while True:
            if len(frames) > 0:
                sock.sendto(frames.pop(0), SOCK_ADDR) #
                print("Sending audio...")
                i += 1
            if i >= N_FRAMES:
                break

    sock.close()

def record(stream, CHUNK):
    i = 0
    with wave.open(IN_FILE, 'r') as rf:
        sample_rate = rf.getframerate()
        frame_width = rf.getsampwidth()
        n_frames = rf.getnframes()
        for _ in range(int(n_frames/CHUNK)):
            frame = rf.readframes(CHUNK)

            frames.append(frame)
            time.sleep(1/sample_rate)
        rf.close()


if __name__ == "__main__":

    Audio = pyaudio.PyAudio()

    stream = Audio.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer = CHUNK,
                    )


    AudioThread = Thread(target = record, args = (stream, CHUNK,))
    udpThread = Thread(target = udpStream)
    AudioThread.setDaemon(True)
    udpThread.setDaemon(True)
    AudioThread.start()
    udpThread.start()
    AudioThread.join()
    udpThread.join()

    stream.close()
