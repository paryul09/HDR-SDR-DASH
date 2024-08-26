import os
import subprocess
import logging
from preprocess_video import  prepare_video_for_fragmentation, fragment_video

#------------extracting audio seprately for info in manifest file
def extract_audio(input_file, output_dir):
    audio_output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}-audio.mp4")
    command = f"ffmpeg -i {input_file} -vn -acodec copy {audio_output_file}"
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Audio extraction successful: {audio_output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error extracting audio: {e}")
        return None
    return audio_output_file


#---creating dash manifest seprately for hdr and sdr--------------------
def create_dash_manifest(output_dir, video_files, mpd_name_hdr="manifest_hdr.mpd", mpd_name_sdr="manifest_sdr.mpd"):
    
    #--------------creating folders---------------------
    final_dir_hdr = os.path.join(output_dir, 'final_hdr')
    final_dir_sdr = os.path.join(output_dir, 'final_sdr')
    os.makedirs(final_dir_hdr, exist_ok=True)
    os.makedirs(final_dir_sdr, exist_ok=True)
    
    logging.info(f"Creating DASH manifests for the following files: {video_files}")
    
    resolutions = ['360p', '480p', '720p', '1080p']
    for res in resolutions:
        os.makedirs(os.path.join(final_dir_hdr, res), exist_ok=True)
        os.makedirs(os.path.join(final_dir_sdr, res), exist_ok=True)
    
    video_fragments_hdr = []
    video_fragments_sdr = []
    
    
    #-------generating fragements and rounding of to nearest 10 of second for consistent fragments---------
    for video_file in video_files:
        if not os.path.exists(video_file):
            logging.error(f"File does not exist: {video_file}")
            continue

        prepared_file = prepare_video_for_fragmentation(video_file, output_dir)
        if not prepared_file:
            logging.error(f"Skipping file due to preparation error: {video_file}")
            continue

        resolution = os.path.splitext(prepared_file)[0].split('_')[-1]
        
        if 'hdr' in prepared_file.lower():
            res_folder = os.path.join(final_dir_hdr, resolution)
            fragmented_file = fragment_video(prepared_file, res_folder)
            
            #----deleting preprocessed file------------
            try:
                os.remove(prepared_file)
                logging.info(f"Deleted HDR file: {prepared_file}")
            except OSError as e:
                logging.error(f"Error deleting HDR file {prepared_file}: {e}")
            if fragmented_file is not None:
                video_fragments_hdr.append(f'[+representation_id=v{resolution}]{fragmented_file}')
            else:
                logging.error(f"Skipping HDR file due to fragmentation error: {prepared_file}")
                
        #---same for sdr files--------
        elif 'sdr' in prepared_file.lower():
            res_folder = os.path.join(final_dir_sdr, resolution)
            fragmented_file = fragment_video(prepared_file, res_folder)
            try:
                os.remove(prepared_file)
                logging.info(f"Deleted SDR file: {prepared_file}")
            except OSError as e:
                logging.error(f"Error deleting SDR file {prepared_file}: {e}")
            if fragmented_file is not None:
                video_fragments_sdr.append(f'[+representation_id=v{resolution}]{fragmented_file}')
            else:
                logging.error(f"Skipping SDR file due to fragmentation error: {prepared_file}")
    
    # Extract and fragment audio for the first video file in both HDR and SDR lists
    audio_fragment_hdr = None
    audio_fragment_sdr = None
    
    #----fetching audio from video files------------
    if any('hdr' in file.lower() for file in video_files):
        audio_file_hdr = extract_audio([file for file in video_files if 'hdr' in file.lower()][0], final_dir_hdr)
        fragmented_audio_file_hdr = fragment_video(audio_file_hdr, final_dir_hdr) if audio_file_hdr else None
        if fragmented_audio_file_hdr:
            audio_fragment_hdr = f'[+representation_id=a1,+language=en]{fragmented_audio_file_hdr}'
            video_fragments_hdr.append(audio_fragment_hdr)
    
    if any('sdr' in file.lower() for file in video_files):
        audio_file_sdr = extract_audio([file for file in video_files if 'sdr' in file.lower()][0], final_dir_sdr)
        fragmented_audio_file_sdr = fragment_video(audio_file_sdr, final_dir_sdr) if audio_file_sdr else None
        if fragmented_audio_file_sdr:
            audio_fragment_sdr = f'[+representation_id=a1,+language=en]{fragmented_audio_file_sdr}'
            video_fragments_sdr.append(audio_fragment_sdr)
    
    #---------------Ensure video fragments and audio fragments are ready---------
    if not video_fragments_hdr:
        logging.error("No HDR video fragments were created. Skipping HDR DASH manifest creation.")
    else:
        command_hdr = (
            f"mp4dash -o {os.path.join(final_dir_hdr, 'manifest')} "
            f"--mpd-name={mpd_name_hdr} "
            f"{' '.join(video_fragments_hdr)}"
        )
        try:
            logging.info(f"Running HDR command: {command_hdr}")
            subprocess.run(command_hdr, shell=True, check=True)
            logging.info(f"HDR DASH manifest created: {os.path.join(final_dir_hdr, mpd_name_hdr)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating HDR DASH manifest: {e}")
    
    if not video_fragments_sdr:
        logging.error("No SDR video fragments were created. Skipping SDR DASH manifest creation.")
    else:
        command_sdr = (
            f"mp4dash -o {os.path.join(final_dir_sdr, 'manifest')} "
            f"--mpd-name={mpd_name_sdr} "
            f"{' '.join(video_fragments_sdr)}"
        )
        try:
            logging.info(f"Running SDR command: {command_sdr}")
            subprocess.run(command_sdr, shell=True, check=True)
            logging.info(f"SDR DASH manifest created: {os.path.join(final_dir_sdr, mpd_name_sdr)}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating SDR DASH manifest: {e}")