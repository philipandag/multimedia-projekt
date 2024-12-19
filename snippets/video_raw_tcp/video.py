import cv2
import socket
import numpy as np
import subprocess

server_ip = '127.0.0.1'
server_port = 12346

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((server_ip, server_port))
sock.listen(1)
print(f"Waiting for connection on {server_ip}:{server_port}...")

client_socket, client_address = sock.accept()
print(f"Connection established with {client_address}")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Camera not found.")
    exit()

frame_width = 640
frame_height = 480
frame_size = frame_width * frame_height * 3

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image.")
        break

    client_socket.sendall(frame.tobytes())

    cv2.imshow("Streaming", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
client_socket.close()
sock.close()
cv2.destroyAllWindows()
