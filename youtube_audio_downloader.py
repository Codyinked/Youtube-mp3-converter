import os
import yt_dlp
import logging
from datetime import datetime

# ✅ Check if StorageUploader is available
try:
    from storage import StorageUploader
    STORAGE_ENABLED = True
except ImportError:
    STORAGE_ENABLED = False

# ✅ Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Ensure the downloads folder exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_audio(youtube_url):
    """Download YouTube audio and save it as MP3."""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_FOLDER}/%(id)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            filename = f"{info_dict['id']}.mp3"
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        logger.info(f"Downloaded: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        return None

def process_download(youtube_url):
    """Download, optionally upload to storage, and return metadata."""
    file_path = download_audio(youtube_url)
    if not file_path:
        return None

    public_url = None

    if STORAGE_ENABLED:
        try:
            uploader = StorageUploader()
            public_url = uploader.upload_file(file_path)
            logger.info(f"File uploaded successfully: {public_url}")
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")

    return {
        "file_path": file_path,
        "public_url": public_url,
        "filename": os.path.basename(file_path),
        "downloaded_at": datetime.utcnow().isoformat()
    }

