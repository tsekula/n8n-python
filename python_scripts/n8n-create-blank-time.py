#!/usr/bin/env python3
"""
Script to create an empty MP3 file with a specified duration.
Requires ffmpy and ffmpeg to be installed.

You can install FFmpeg directly on your system, or use a Python package
that includes FFmpeg binaries like imageio-ffmpeg:
    pip install imageio-ffmpeg
"""

import os
import sys
import argparse
import shutil
from ffmpy import FFmpeg, FFRuntimeError

def get_ffmpeg_path():
    """
    Try to find the FFmpeg executable from various sources.
    First checks if it's in PATH, then tries to get it from imageio-ffmpeg if installed.
    
    Returns:
        str or None: Path to ffmpeg executable or None if not found
    """
    # First check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    
    # Try to get ffmpeg from imageio-ffmpeg if installed
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        return get_ffmpeg_exe()
    except ImportError:
        pass
    
    # If we get here, ffmpeg was not found
    return None

def create_empty_audio(duration, output_file="empty_audio.mp3", ffmpeg_path=None):
    """
    Create an empty MP3 file with the specified duration.
    
    Args:
        duration (int): Duration of the audio file in seconds
        output_file (str, optional): Path to the output file. Defaults to "empty_audio.mp3".
        ffmpeg_path (str, optional): Path to ffmpeg executable. If None, will try to find it.
    
    Returns:
        str: Path to the created file or None if creation failed
    """
    try:
        # Check if ffmpeg is available
        if ffmpeg_path is None:
            ffmpeg_path = get_ffmpeg_path()
            if ffmpeg_path is None:
                print("ERROR: FFmpeg not found. Please install FFmpeg or provide the path to the executable.")
                print("Options:")
                print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
                print("2. For Windows users: choco install ffmpeg")
                print("3. Install imageio-ffmpeg package: pip install imageio-ffmpeg")
                return None
        
        # Create an empty audio file using ffmpeg
        ff = FFmpeg(
            executable=ffmpeg_path,
            inputs={f"anullsrc=r=44100:cl=stereo": "-f lavfi"},
            outputs={output_file: f"-t {duration} -c:a libmp3lame -b:a 128k"}
        )
        
        print(f"Executing command: {ff.cmd}")
        ff.run()
        
        if os.path.exists(output_file):
            print(f"Successfully created empty audio file: {output_file} ({duration} seconds)")
            return output_file
        else:
            print("Failed to create audio file")
            return None
    except FFRuntimeError as e:
        print(f"FFmpeg Runtime Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error creating empty audio file: {str(e)}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an empty MP3 file with specified duration")
    parser.add_argument("duration", type=int, help="Duration of the audio file in seconds")
    parser.add_argument("-o", "--output", default="empty_audio.mp3", help="Output file path (default: empty_audio.mp3)")
    parser.add_argument("--ffmpeg", help="Path to ffmpeg executable (if not in PATH)")
    
    args = parser.parse_args()
    
    result = create_empty_audio(args.duration, args.output, args.ffmpeg)
    if result is None:
        sys.exit(1)
