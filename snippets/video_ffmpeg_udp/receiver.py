import cv2
import numpy as np
import subprocess


ffmpeg_command = [
    'ffmpeg',
    '-i', 'udp://127.0.0.1:12345',  # The same UDP address as the server
    '-f', 'rawvideo',  # Output format: raw video frames
    '-pix_fmt', 'bgr24',  # Pixel format to match OpenCV's BGR format
    '-vcodec', 'rawvideo',  # No codec; just raw video
    '-an',  # Disable audio (since we're just handling video)
    '-sn',  # Disable subtitle handling
    '-r', '30',  # Frame rate
    '-',  # Output to stdout (pipe)
]

ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

frame_width = 640
frame_height = 480

while True:
    raw_frame = ffmpeg_process.stdout.read(frame_width * frame_height * 3)

    if not raw_frame:
        break

    frame = np.frombuffer(raw_frame, dtype=np.uint8).reshape((frame_height, frame_width, 3))

    cv2.imshow("Received Stream", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

ffmpeg_process.stdout.close()
ffmpeg_process.stderr.close()
ffmpeg_process.wait()
cv2.destroyAllWindows()
