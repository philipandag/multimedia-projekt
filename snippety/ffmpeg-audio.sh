#!/bin/bash
# Streams an audio file over UDP to a local port and receives it back

INPUT_FILE=$1    # Input .wav file to stream
UDP_PORT=12748           # Port for UDP transmission

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Input file $INPUT_FILE not found!"
  exit 1
fi

duration=$(ffprobe -i "$INPUT_FILE" -show_entries format=duration -v quiet -of csv="p=0")
echo "Duration: $duration"
ffmpeg -i "udp://localhost:$UDP_PORT" -acodec pcm_s16le -ar 16000 -f wav -t "$duration" received_udp.wav &
UDP_PID=$!
sleep 2
ffmpeg -re -i "$INPUT_FILE" -acodec pcm_s16le -ar 16000 -f wav "udp://localhost:$UDP_PORT" &> /dev/null
wait $UDP_PID

