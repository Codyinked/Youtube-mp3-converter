import os
import yt_dlp
import logging
from datetime import datetime

# ✅ Ensure the downloads folder exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ✅ Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Specify FFmpeg location (Ensure Railway has it installed)
FFMPEG_LOCATION = "/usr/bin/ffmpeg"  # Default Linux path, adjust if needed

def download_audio(youtube_url):
    """Download YouTube audio and save it as MP3 using yt-dlp."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "ffmpeg_location": FFMPEG_LOCATION,  # ✅ Explicitly specify FFmpeg location
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            filename = f"{info_dict['id']}.mp3"
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        logger.info(f"Downloaded and converted: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return None

