import pyaudio
import socket

FORMAT = pyaudio.paInt16
CHUNK = 128
CHANNELS = 1
RATE = 8000

SOCK = socket.SOCK_DGRAM
N_FRAMES=16000/CHUNK

PORT=12345