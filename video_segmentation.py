import os
import logging
from transcode_and_watermark import transcode_and_watermark
from convert_hdr_to_sdr import convert_hdr_to_sdr
from detect import is_hdr
from manifest_creation import fragment_video, create_dash_manifest

def main(input_file, output_dir):
    
    """
    Main function to handle 
        video processing,
        including transcoding,
        HDR/SDR conversion,
        and watermarking,
        generating mpd file
    """
    
    #------------creating output dir----------------
    video_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(input_file), f"output_{video_name}")
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"Output directory created: {output_dir}")
    
    
    resolutions = [(360, 480), (480, 640), (720, 1280), (1080, 1920)]
    
    # #-----check if file is hdr or sdr-------------
    is_hdr_flag = is_hdr(input_file)

    hdr_output_dir = os.path.join(output_dir, "hdr")
    sdr_output_dir = os.path.join(output_dir, "sdr")

    #------------------Create necessary directories----------------------
    os.makedirs(hdr_output_dir, exist_ok=True)
    os.makedirs(sdr_output_dir, exist_ok=True)

    output_folder = hdr_output_dir if is_hdr_flag else sdr_output_dir

    #--------------Transcode video to multiple resolutions with watermarking-----------------------
    transcode_and_watermark(input_file, output_folder, resolutions, is_hdr_flag)

    #--------------Convert to SDR if HDR file------------------------
    if is_hdr_flag:
        sdr_file_name = convert_hdr_to_sdr(input_file, sdr_output_dir)
        if sdr_file_name:
            transcode_and_watermark(sdr_file_name, sdr_output_dir, resolutions, False)
            try:
                os.remove(sdr_file_name)
                logging.info(f"Deleted SDR file: {sdr_file_name}")
            except OSError as e:
                logging.error(f"Error deleting SDR file {sdr_file_name}: {e}")
        else:
            logging.error("Error in SDR file generation")

    #------------------Fragment videos and create DASH manifest--------------------
    video_files = []
    for folder in [hdr_output_dir, sdr_output_dir]:
        for file in os.listdir(folder):
            if file.endswith(".mp4"):
                input_file_path = os.path.join(folder, file)
                video_files.append(input_file_path)

    if video_files:
        create_dash_manifest(output_dir, video_files)


if __name__ == "__main__":
    #--------provide input video file path---------
    input_file = "vi_f.mp4"
    main(input_file, None)

