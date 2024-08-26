Video Segmentation and DASH Manifest Creation
This Python script processes video files by transcoding them into multiple resolutions, converting HDR to SDR if needed, adding watermarks, and generating DASH-compatible manifest files using ffmpeg and Bento4.
Prerequisites
Ensure the following dependencies are installed on your system:
FFmpeg:
FFmpeg is required for transcoding, watermarking, and converting HDR videos to SDR.
sudo apt-get install ffmpeg
libzimg-dev:
This library is required for the zscale filter used in HDR to SDR conversion.
Bento4:
Bento4 is required for fragmenting videos and creating DASH manifests.
You can download and install Bento4 from here.
Script Usage
Running the Script
To use the script, simply pass the path to your video file as the first argument when running the video_segmentation.py script.
Example
python3 video_segmentation.py /path/to/your/video_file.mp4
What the Script Does
Creates Output Directory:
The script creates an output directory in the same location as your video file named output_<video_name>.
Transcodes Video:
The video is transcoded into multiple resolutions (360p, 480p, 720p, 1080p) with appropriate watermarks.
If the video is HDR, it also converts the video to SDR.
Converts HDR to SDR:
If the video is detected as HDR, it converts the HDR video to SDR using the zscale filter.
Fragments Videos and Generates DASH Manifest:
The transcoded videos are fragmented, and a DASH manifest is created for both HDR and SDR content.
Project Structure
video_segmentation.py: Main script that processes the video and generates the output.
transcode_and_watermark.py: Contains functions to transcode videos and add watermarks.
convert_hdr_to_sdr.py: Contains functions to convert HDR videos to SDR.
detect.py: Contains functions to detect if a video is HDR.
manifest_creation.py: Contains functions to fragment videos and create DASH manifests.
Logging
The script logs all major steps and any errors encountered during processing. Check the logs for detailed information about the processing.
