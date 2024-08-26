import subprocess
import os
import logging

def transcode_and_watermark(input_file, output_dir, resolutions, is_hdr):
    """Transcodes a video file to multiple resolutions and adds a watermark (circle)."""
    logging.info(f"Transcoding and watermarking video: {input_file}")
    
    #-----------Fixed frame rate and key frame interval for all resolutions------------
    output_files = []
    frame_rate = 30  
    keyframe_interval = 60  

    #----------depending on hdr or sdr adding watermark-----------------
    for height, width in resolutions:
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}_{'hdr' if is_hdr else 'sdr'}_{height}p.mp4")
        radius = int(height * (0.07 if is_hdr else 0.05))
        x_position = f"(w-text_w)-{radius}"
        y_position = f"{radius}" if is_hdr else f"(h-text_h)-{radius}"
        color = "green" if is_hdr else "white"
        circle_filter = f"drawtext=fontfile=/usr/share/fonts/truetype/freefont/FreeSansBold.ttf:text=◯:fontcolor={color}:fontsize={radius*2}:x={x_position}:y={y_position}"

        command = (
            f"ffmpeg -i {input_file} -r {frame_rate} -g {keyframe_interval} -keyint_min {keyframe_interval} "
            f"-sc_threshold 0 -c:v libx265 -vf 'scale={width}:{height}:force_original_aspect_ratio=decrease,{circle_filter}' "
            f"-b:v 2M -preset fast -crf 22 {output_file}"
        )
        
        try:
            subprocess.run(command, shell=True, check=True)
            output_files.append(output_file)
            logging.info(f"Transcoding and watermarking successful: {output_file}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error transcoding video: {e}")

    return output_files
