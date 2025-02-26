import os
import sys
import logging
import re
import time
import yt_dlp
from pydub import AudioSegment
from tqdm import tqdm
from utils import validate_url, create_output_directory, sanitize_filename

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def my_hook(d):
    """Custom progress hook for yt-dlp"""
    if d['status'] == 'downloading':
        try:
            percent = d['_percent_str']
            logger.info(f"Download Progress: {percent}")
        except Exception:
            pass
    elif d['status'] == 'finished':
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

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'verbose': True,  # Enable verbose output for debugging
            'progress_hooks': [my_hook],  # Add progress hook
            'retries': 10,  # Number of retries for network errors
            'fragment_retries': 10,  # Number of retries for stream fragments
            'extractor_retries': 10,  # Number of retries for extractor errors
            'file_access_retries': 10,  # Number of retries for file access
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        logger.info(f"Fetching video information from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # Get video info first
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not fetch video information")

                video_title = sanitize_filename(info.get('title', 'unknown_video'))
                logger.info(f"Video title: {video_title}")

                # Download and convert to MP3
                logger.info("Starting download and conversion...")
                ydl.download([url])

                # The file will be automatically converted to MP3 by yt-dlp
                mp3_file = os.path.join(output_dir, f"{video_title}.mp3")

                if os.path.exists(mp3_file):
                    logger.info(f"Success! File saved as: {mp3_file}")
                    print(f"\nSuccess! File saved as: {mp3_file}")
                    return mp3_file
                else:
                    logger.error("MP3 file not found after download")
                    raise Exception("MP3 file not found after download")

            except Exception as e:
                logger.error(f"Error during yt-dlp operation: {str(e)}")
                raise

    except Exception as e:
        logger.error(f"Error during download/conversion: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
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