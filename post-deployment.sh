chown -R node:node /data/files && chmod -R 755 /data/files
#!/bin/bash

# Install FFmpeg
apk add --no-cache ffmpeg

# Set environment variables
export FFMPEG_BINARY=/usr/bin/ffmpeg
export IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg

# Install requirements
pip install -r /data/requirements.txt