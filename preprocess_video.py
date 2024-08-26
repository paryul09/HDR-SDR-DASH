import os
import subprocess
import logging


def get_rounded_duration(video_file):
    command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_file}"
    try:
        output = subprocess.check_output(command, shell=True, text=True).strip()
        duration = float(output)
        #--------------Round to the nearest 1/100th of a second----------
        rounded_duration = round(duration, 2)
        logging.info(f"Original Duration: {duration} seconds, Rounded Duration: {rounded_duration} seconds")
        return rounded_duration
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting duration for {video_file}: {e}")
        return None
    
def trim_video(input_file, output_file, duration):
    """-----------Trim a video file to a specified duration.------------"""
    command = f"ffmpeg -i {input_file} -t {duration} -c copy {output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Trimmed {input_file} to {duration} seconds. Output: {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error trimming video {input_file}: {e}")


def prepare_video_for_fragmentation(input_file, output_dir):
    rounded_duration = get_rounded_duration(input_file)
    if rounded_duration is None:
        logging.error("Failed to round duration. Skipping video preparation.")
        return None
    trimmed_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.mp4")
    trim_video(input_file, trimmed_file, rounded_duration)
    
    return trimmed_file

def fragment_video(input_file, output_dir, fragment_duration=7500):
    
    """Fragments a video or audio file into smaller segments of 7.5 sec each"""
    
    output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}-frag.mp4")
    command = f"mp4fragment --fragment-duration {fragment_duration} {input_file} {output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Fragmentation successful: {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fragmenting file: {e}")
        return None
    return output_file