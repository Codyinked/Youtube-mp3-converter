#!/usr/bin/env python3

import os
import sys
import logging
import re
import time
from pytube import YouTube
from pydub import AudioSegment
from tqdm import tqdm
from utils import validate_url, create_output_directory, sanitize_filename

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_progress_bar(stream, chunk, bytes_remaining):
    """Callback function to update download progress bar"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    sys.stdout.write(f"\rDownloading... {percentage:.1f}%")
    sys.stdout.flush()

def get_video_id(url):
    """Extract video ID from URL"""
    try:
        # Extract video ID from URL query parameters
        video_id = None
        if 'youtube.com' in url:
            query = url.split('?')[1]
            params = dict(param.split('=') for param in query.split('&'))
            video_id = params.get('v')
        elif 'youtu.be' in url:
            video_id = url.split('/')[-1]
        return video_id
    except Exception:
        return None

def get_audio_stream(yt, retries=3):
    """Get audio stream with retry mechanism"""
    for attempt in range(retries):
        try:
            # Try different stream selection strategies
            streams = yt.streams.filter(only_audio=True)
            if not streams:
                raise Exception("No audio streams available")

            # First try: highest bitrate audio
            audio_stream = streams.order_by('abr').desc().first()
            if audio_stream:
                return audio_stream

            # Second try: any audio stream
            audio_stream = streams.first()
            if audio_stream:
                return audio_stream

            if attempt < retries - 1:
                logger.warning(f"Retry {attempt + 1}/{retries} for stream selection")
                time.sleep(1)  # Wait before retry

        except Exception as e:
            if attempt < retries - 1:
                logger.warning(f"Stream selection failed (attempt {attempt + 1}/{retries}): {str(e)}")
                time.sleep(1)  # Wait before retry
            else:
                raise

    raise Exception("Failed to get audio stream after all retries")

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
        # Create YouTube object with retries
        logger.info(f"Fetching video information from: {url}")
        attempts = 3
        for attempt in range(attempts):
            try:
                yt = YouTube(url, on_progress_callback=show_progress_bar)
                break
            except Exception as e:
                if attempt == attempts - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{attempts} for video info: {str(e)}")
                time.sleep(1)

        try:
            # Try to get video title
            video_title = yt.title
            logger.info(f"Video title: {video_title}")
        except Exception as e:
            # Fallback to video ID if title is not accessible
            video_id = get_video_id(url) or 'unknown'
            video_title = f"youtube_audio_{video_id}"
            logger.warning(f"Could not get video title, using fallback: {video_title}")

        # Sanitize the filename
        video_title = sanitize_filename(video_title)

        # Get audio stream with retries
        logger.info("Selecting audio stream...")
        audio_stream = get_audio_stream(yt)

        # Create output directory if it doesn't exist
        create_output_directory(output_dir)
        logger.info(f"Using output directory: {output_dir}")

        # Download the audio file
        logger.info("Starting download...")
        temp_file = audio_stream.download(output_path=output_dir, filename=f"{video_title}.tmp")
        logger.info(f"Downloaded temporary file: {temp_file}")

        # Convert to MP3
        logger.info("Converting to MP3...")
        audio = AudioSegment.from_file(temp_file)
        mp3_file = os.path.join(output_dir, f"{video_title}.mp3")

        # Export as MP3 with 192kbps bitrate
        audio.export(mp3_file, format="mp3", bitrate="192k")
        logger.info(f"MP3 conversion complete: {mp3_file}")

        # Clean up temporary file
        os.remove(temp_file)
        logger.info("Temporary file cleaned up")

        print(f"\nSuccess! File saved as: {mp3_file}")
        return mp3_file

    except Exception as e:
        logger.error(f"Error during download/conversion: {str(e)}")
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