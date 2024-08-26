import subprocess
import os
import logging

def convert_hdr_to_sdr(hdr_video_path, output_dir):  
    logging.info(f"Converting HDR to SDR: {hdr_video_path}")
    
    filename = os.path.basename(hdr_video_path)
    sdr_output_filename = f"{os.path.splitext(filename)[0]}_sdr.mp4"
    sdr_output_file = os.path.join(output_dir, sdr_output_filename)

    sdr_command = (
        f"ffmpeg -i {hdr_video_path} "
        f"-vf 'zscale=t=linear:npl=100,format=gbrpf32le,"
        f"zscale=p=bt709,tonemap=hable:desat=0.9,"
        f"zscale=t=bt709:m=bt709:r=tv,format=yuv420p' "
        f"-r 30 -g 48 -c:v libx265 -crf 22 -preset fast "
        f"{sdr_output_file}"
    )

    try:
        subprocess.run(sdr_command, shell=True, check=True)
        logging.info(f"HDR to SDR conversion successful: {sdr_output_file}")
        return sdr_output_file
    except subprocess.CalledProcessError as e:
        logging.error(f"Error converting HDR to SDR: {e}")
        return None
