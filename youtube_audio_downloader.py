import os
import sys
import logging
import re
import time
import yt_dlp
from pydub import AudioSegment
from tqdm import tqdm
from urllib.parse import urlparse, parse_qs
from utils import validate_url, create_output_directory, sanitize_filename
from database import insert_download_record
from storage import StorageUploader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize storage uploader
storage = StorageUploader()

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    return None

def my_hook(d):
    """Custom progress hook for yt-dlp"""
    if d['status'] == 'downloading':
        try:
            percent = d['_percent_str']
            speed = d.get('speed', 0)
            if speed:
                speed_str = f"{speed/1024/1024:.1f} MB/s"
                print(f"\rDownload Progress: {percent} at {speed_str}", end='', flush=True)
            else:
                print(f"\rDownload Progress: {percent}", end='', flush=True)
        except Exception:
            pass
    elif d['status'] == 'finished':
        print("\nDownload completed, starting conversion...")
        logger.info('Download completed, starting conversion...')

def download_audio(url, output_dir="downloads"):
    """
    Download audio from YouTube video and convert to MP3

    Args:
        url (str): YouTube video URL
        output_dir (str): Directory to save the output file

    Returns:
        str: Path to the downloaded MP3 file
    """
    try:
        # Create output directory if it doesn't exist
        create_output_directory(output_dir)
        logger.info(f"Using output directory: {output_dir}")

        # Extract video ID
        video_id = get_video_id(url)
        if not video_id:
            raise Exception("Could not extract video ID from URL")

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'verbose': True,
            'progress_hooks': [my_hook],
            'retries': 10,
            'fragment_retries': 10,
            'extractor_retries': 10,
            'file_access_retries': 10,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        print(f"\nFetching video information from: {url}")
        logger.info(f"Fetching video information from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not fetch video information")

                video_title = sanitize_filename(info.get('title', 'unknown_video'))
                print(f"Video title: {video_title}")
                logger.info(f"Video title: {video_title}")

                # Download and convert to MP3
                logger.info("Starting download and conversion...")
                ydl.download([url])

                # The file will be automatically converted to MP3 by yt-dlp
                mp3_file = os.path.join(output_dir, f"{video_title}.mp3")
                logger.info(f"Checking for MP3 file at: {mp3_file}")

                # Check if file exists and has size greater than 0
                if os.path.exists(mp3_file):
                    file_size = os.path.getsize(mp3_file)
                    logger.info(f"Found MP3 file. Size: {file_size} bytes")
                    print(f"\nSuccess! File saved as: {mp3_file}")

                    # Upload to Supabase Storage
                    print("Uploading to Supabase Storage...")
                    public_url = storage.upload_file(mp3_file)

                    if public_url:
                        print("File uploaded successfully!")
                        print(f"Public URL: {public_url}")
                    else:
                        print("Warning: Failed to upload file to storage")

                    # Record the download in the database
                    if insert_download_record(video_id, video_title, mp3_file, public_url):
                        logger.info("Download recorded in database")
                        print("Download recorded in database")
                    else:
                        logger.warning("Failed to record download in database")
                        print("Warning: Failed to record download in database")

                    return mp3_file
                else:
                    # Check for alternative file name (with underscores instead of parentheses)
                    alt_title = video_title.replace('(', '_').replace(')', '_')
                    alt_mp3_file = os.path.join(output_dir, f"{alt_title}.mp3")

                    if os.path.exists(alt_mp3_file):
                        logger.info(f"Found MP3 file with alternative name: {alt_mp3_file}")
                        return alt_mp3_file

                    logger.error(f"MP3 file not found. Checked paths:\n{mp3_file}\n{alt_mp3_file}")
                    raise Exception(f"MP3 file not found or empty after download: {mp3_file}")

            except Exception as e:
                logger.error(f"Error during yt-dlp operation: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Error during download/conversion: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        print(f"\nError: {str(e)}")
        return None

def main():
    """Main function to handle both command-line and interactive input"""
    print("YouTube Audio Downloader")
    print("=" * 50)

    # Check for command-line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
        logger.info(f"URL provided via command line: {url}")
        if validate_url(url):
            download_audio(url)
        else:
            logger.error("Invalid YouTube URL provided via command line")
            sys.exit(1)
        return

    # Interactive mode
    while True:
        # Get URL from user
        url = input("\nEnter YouTube URL (or 'q' to quit): ").strip()

        if url.lower() == 'q':
            print("Goodbye!")
            break

        # Validate URL
        if not validate_url(url):
            print("Error: Invalid YouTube URL")
            continue

        # Download and convert
        output_file = download_audio(url)

        if output_file:
            print("\nReady for next download!")
        else:
            print("\nDownload failed. Please try again.")

        print("=" * 50)

if __name__ == "__main__":
    main()