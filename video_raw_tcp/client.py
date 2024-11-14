import cv2
import numpy as np
import socket

server_ip = '127.0.0.1'
server_port = 12346
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server_ip, server_port))

frame_width = 640
frame_height = 480
frame_size = frame_width * frame_height * 3

buffer = b''

while True:
    while len(buffer) < frame_size:
        data = sock.recv(frame_size - len(buffer))
        if not data:
            print("Connection closed by server.")
            break 
        buffer += data 

    if len(buffer) == frame_size:
        frame = np.frombuffer(buffer, dtype=np.uint8).reshape((frame_height, frame_width, 3))
        cv2.imshow("Received Stream", frame)
        buffer = b''

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
sock.close()
cv2.destroyAllWindows()
