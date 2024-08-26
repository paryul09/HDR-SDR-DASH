import subprocess
import json
import logging

def is_hdr(video_path):
    
    """Detects if a video file is likely HDR or not based on metadata."""
    
    logging.info(f"Checking if the video is HDR: {video_path}")
    cmd = f"ffprobe -v quiet -print_format json -show_entries stream=codec_name,bit_rate,width,height,pix_fmt,color_range,color_primaries,transfer_characteristics,matrix_coefficients {video_path}"
    try:
        output = subprocess.check_output(cmd, shell=True, text=True)
        data = json.loads(output)
        video_stream = data['streams'][0]
        codec_name = video_stream['codec_name']
        color_range = video_stream.get('color_range', 'unknown')
        color_primaries = video_stream.get('color_primaries', 'unknown')
        transfer_characteristics = video_stream.get('transfer_characteristics', 'unknown')
        matrix_coefficients = video_stream.get('matrix_coefficients', 'unknown')
        if color_range == 'limited':
            return False
        if codec_name in ['hevc', 'libx265']:
            return True
        if color_primaries == 'bt2020':
            return True
        if transfer_characteristics == 'bt2020_12':
            return True
        if matrix_coefficients == 'bt2020':
            return True

        logging.info("Video is likely SDR")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error checking HDR status: {e}")
        return False
