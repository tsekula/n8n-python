# code for n8n Python Code node
# creates an empty audio file with specified duration and parameters

import ffmpy
import os
import subprocess
import time

results = []

# Function to create empty audio
def create_empty_audio_file(
    duration,
    sample_rate=44100,
    bitrate='192k',
    channels=2,
    output_format='mp3',
    output_path='.',
    filename='empty_audio'
):
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    # Construct output filename
    output_file = os.path.join(output_path, f"{filename}.{output_format}")
    
    # Correct ffmpy command for generating silent audio
    # Note: 'anullsrc=r={sample_rate}:cl=stereo' needs to match channel count
    channel_layout = 'stereo' if channels == 2 else 'mono'
    
    ff = ffmpy.FFmpeg(
        global_options=['-y'],  # Global option to overwrite files
        inputs={
            f'anullsrc=r={sample_rate}:cl={channel_layout}': ['-f', 'lavfi', '-t', str(duration)]
        },
        outputs={
            output_file: [
                '-ar', str(sample_rate),  # Sample rate
                '-ab', bitrate,          # Bitrate
                '-ac', str(channels)     # Number of channels
            ]
        }
    )
    
    # Run the command and capture output
    try:
        ff.run(stderr=subprocess.PIPE)
        return output_file, None
    except ffmpy.FFRuntimeError as e:
        return None, str(e)

# Main code for n8n
try:
    # Get parameters from the first item
    item = items[0]
    
    # Extract parameters
    duration = float(item.get('audio_duration', 10))
    sample_rate = int(item.get('audio_sampling_rate', 44100))
    bitrate = item.get('audio_bitrate', '192k')
    channels = int(item.get('audio_channels', 2))
    output_format = item.get('audio_file_format', 'mp3')
    output_path = item.get('audio_files_path', '.')
    filename = item.get('audio_file_name', 'empty_audio')
    
    # Create the audio file
    output_file, error = create_empty_audio_file(
        duration=duration,
        sample_rate=sample_rate,
        bitrate=bitrate,
        channels=channels,
        output_format=output_format,
        output_path=output_path,
        filename=filename
    )
    
    # Update the item with results
    if error is None:
        item['audio_output_status'] = 'success'
        item['audio_output_file'] = output_file
    else:
        item['audio_output_status'] = 'error'
        item['audio_output_error'] = error
    
    results.append(item)
    return results
    
except Exception as e:
    # Handle any unexpected errors
    return [{'status': 'error', 'error': str(e)}]
