import yt_dlp
import os

def process_download(youtube_url, output_dir="downloads"):
    """
    Downloads a YouTube video as MP3.

    Args:
        youtube_url (str): The URL of the YouTube video.
        output_dir (str): Directory to save the MP3 file.

    Returns:
        str: Path to the downloaded MP3 file, or None if download fails.
    """
    os.makedirs(output_dir, exist_ok=True)  # ✅ Ensure the output directory exists
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "ffmpeg_location": "/usr/bin/ffmpeg",  # ✅ Ensure FFmpeg is correctly referenced
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            file_path = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            return file_path  # ✅ Return the path of the downloaded MP3 file

    except Exception as e:
        print(f"Error downloading video: {str(e)}")
        return None
