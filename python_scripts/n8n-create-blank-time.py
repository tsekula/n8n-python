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

def create_empty_audio(
    duration, 
    output_file="empty_audio.mp3", 
    ffmpeg_path=None, 
    sample_rate=44100, 
    bitrate=128, 
    channels=2, 
    output_format="mp3",
    output_dir=None
):
    """
    Create an empty audio file with the specified parameters.
    
    Args:
        duration (int): Duration of the audio file in seconds
        output_file (str, optional): Name of the output file. Defaults to "empty_audio.mp3".
        ffmpeg_path (str, optional): Path to ffmpeg executable. If None, will try to find it.
        sample_rate (int, optional): Sampling rate in Hz. Defaults to 44100.
        bitrate (int, optional): Audio bitrate in kbps. Defaults to 128.
        channels (int, optional): Number of audio channels (1=mono, 2=stereo). Defaults to 2.
        output_format (str, optional): Output file format (mp3, wav, ogg, etc). Defaults to "mp3".
        output_dir (str, optional): Directory to save the output file. Defaults to current directory.
    
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
        
        # Set channel layout based on number of channels
        channel_layout = "mono" if channels == 1 else "stereo"
        
        # Ensure output file has the correct extension
        if not output_file.endswith(f".{output_format}"):
            base_name = os.path.splitext(output_file)[0]
            output_file = f"{base_name}.{output_format}"
        
        # If output directory is specified, combine with filename
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_file)
        
        # Create an empty audio file using ffmpeg
        ff = FFmpeg(
            executable=ffmpeg_path,
            inputs={f"anullsrc=r={sample_rate}:cl={channel_layout}": "-f lavfi"},
            outputs={output_file: f"-t {duration} -c:a {get_codec_for_format(output_format)} -b:a {bitrate}k"}
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

def get_codec_for_format(output_format):
    """
    Returns the appropriate audio codec for the given output format.
    
    Args:
        output_format (str): The output format (mp3, wav, ogg, etc.)
        
    Returns:
        str: The codec name to use with FFmpeg
    """
    format_codec_map = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "ogg": "libvorbis",
        "aac": "aac",
        "flac": "flac",
        "m4a": "aac"
    }
    
    return format_codec_map.get(output_format.lower(), "libmp3lame")

def n8n_execute(params):
    """
    Function to be called from n8n Python code node.
    
    Args:
        params (dict): Dictionary containing parameters for audio creation
            - duration (int): Duration in seconds (required)
            - output_file (str): Output filename (optional)
            - sample_rate (int): Sample rate in Hz (optional)
            - bitrate (int): Audio bitrate in kbps (optional)
            - channels (int): Number of audio channels (optional)
            - output_format (str): Output file format (optional)
            - output_dir (str): Output directory (optional)
            - ffmpeg_path (str): Path to FFmpeg executable (optional)
    
    Returns:
        dict: Result containing success status and file path
    """
    try:
        # Extract parameters with defaults
        duration = params.get('duration')
        if duration is None:
            return {"success": False, "error": "Duration parameter is required"}
        
        output_file = params.get('output_file', 'empty_audio.mp3')
        sample_rate = params.get('sample_rate', 44100)
        bitrate = params.get('bitrate', 128)
        channels = params.get('channels', 2)
        output_format = params.get('output_format', 'mp3')
        output_dir = params.get('output_dir')
        ffmpeg_path = params.get('ffmpeg_path')
        
        # Create the audio file
        result_path = create_empty_audio(
            duration=duration,
            output_file=output_file,
            ffmpeg_path=ffmpeg_path,
            sample_rate=sample_rate,
            bitrate=bitrate,
            channels=channels,
            output_format=output_format,
            output_dir=output_dir
        )
        
        if result_path:
            return {
                "success": True,
                "file_path": result_path,
                "duration": duration,
                "format": output_format,
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "channels": channels
            }
        else:
            return {"success": False, "error": "Failed to create audio file"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an empty audio file with specified parameters")
    parser.add_argument("duration", type=int, help="Duration of the audio file in seconds")
    parser.add_argument("-o", "--output", default="empty_audio.mp3", help="Output file path (default: empty_audio.mp3)")
    parser.add_argument("--ffmpeg", help="Path to ffmpeg executable (if not in PATH)")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Sample rate in Hz (default: 44100)")
    parser.add_argument("--bitrate", type=int, default=128, help="Audio bitrate in kbps (default: 128)")
    parser.add_argument("--channels", type=int, default=2, help="Number of audio channels (1=mono, 2=stereo) (default: 2)")
    parser.add_argument("--format", default="mp3", help="Output file format (mp3, wav, ogg, etc.) (default: mp3)")
    parser.add_argument("--output-dir", help="Directory to save the output file")
    
    args = parser.parse_args()
    
    result = create_empty_audio(
        args.duration, 
        args.output, 
        args.ffmpeg,
        args.sample_rate,
        args.bitrate,
        args.channels,
        args.format,
        args.output_dir
    )
    
    if result is None:
        sys.exit(1)

# Example of how to use this in an n8n Python Code node:
"""
# n8n Python Code node example:
import json

# Get input data
input_data = $input.item.json

# Set parameters for audio creation
params = {
    'duration': input_data.get('duration', 10),  # Duration in seconds
    'output_file': input_data.get('filename', 'empty_audio.mp3'),
    'sample_rate': input_data.get('sample_rate', 44100),
    'bitrate': input_data.get('bitrate', 128),
    'channels': input_data.get('channels', 2),
    'output_format': input_data.get('format', 'mp3'),
    'output_dir': input_data.get('output_dir', '/tmp')
}

# Call the function
result = n8n_execute(params)

# Return the result
return result
"""
