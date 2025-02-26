from flask import Flask, request, jsonify
import os
from youtube_audio_downloader import download_audio
from database import insert_download_record
from storage import StorageUploader
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
storage = StorageUploader()

# Ensure downloads directory exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "YouTube to MP3 Converter API is running"
    })

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        youtube_url = data.get("youtube_url")

        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        # Use our existing download function
        logger.info(f"Processing download request for URL: {youtube_url}")
        output_file = download_audio(youtube_url, DOWNLOAD_FOLDER)

        if not output_file:
            return jsonify({"error": "Failed to download and convert video"}), 500

        # Upload to Supabase Storage
        logger.info("Uploading to Supabase Storage...")
        public_url = storage.upload_file(output_file)

        if not public_url:
            return jsonify({"error": "Failed to upload file to storage"}), 500

        return jsonify({
            "success": True,
            "file_path": output_file,
            "mp3_url": public_url
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # ALWAYS serve the app on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)