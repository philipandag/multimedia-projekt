import cv2
import socket
import subprocess
import numpy as np

# Initialize socket
server_ip = '127.0.0.1'  # Localhost for testing
server_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((server_ip, server_port))

# Initialize camera
cap = cv2.VideoCapture(0)  # 0 is the default camera

if not cap.isOpened():
    print("Error: Camera not found.")
    exit()

# Set up FFmpeg process for encoding the frames
ffmpeg_command = [
    'ffmpeg',
    '-y',  # Overwrite output file if it exists
    '-f', 'rawvideo',  # Input format (raw video)
    '-vcodec', 'rawvideo',  # Specify raw video codec
    '-pix_fmt', 'bgr24',  # Pixel format (OpenCV uses BGR24 by default)
    '-s', '640x480',  # Video size (can change to your camera's resolution)
    '-r', '30',  # Frame rate
    '-i', '-',  # Input will be provided via stdin (pipes)
    '-f', 'mpegts',  # Output format
    '-codec:v', 'mpeg1video',  # Video codec (MPEG1 for streaming)
    '-b:v', '500k',  # Video bitrate
    '-muxdelay', '0.1',  # Small delay between packets
    'udp://127.0.0.1:12345'  # Destination address (UDP)
]

# Start the FFmpeg process
ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

while True:
    # Capture frame-by-frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to capture image.")
        break

    # Send the frame to FFmpeg for encoding and streaming
    ffmpeg_process.stdin.write(frame.tobytes())

    # Optionally, display the frame locally (for debugging)
    cv2.imshow("Streaming", frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
sock.close()
cv2.destroyAllWindows()
ffmpeg_process.stdin.close()
ffmpeg_process.wait()
