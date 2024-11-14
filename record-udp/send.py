import pyaudio
import socket
from threading import Thread
from defines import *
import wave
import struct

frames = []
SOCK_ADDR=("127.0.0.1", PORT)
OUT_FILE="recording-original.wav"

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
    with wave.open(OUT_FILE, 'w') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)

        while True:
            frame = stream.read(CHUNK)
            wf.writeframes(frame)
            frames.append(frame)
            i += 1
            if i >= N_FRAMES:
                break
        wf.close()


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
