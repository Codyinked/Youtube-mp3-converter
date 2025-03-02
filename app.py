from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from youtube_audio_downloader import download_audio
from database import insert_download_record
from storage import StorageUploader

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize Flask app & CORS
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app, resources={r"/convert": {"origins": "*"}})  # ✅ Allow all frontend requests

# ✅ Ensure downloads directory exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def serve_frontend():
    """ Serve the frontend index.html from root """
    try:
        return send_from_directory(os.getcwd(), "index.html")
    except Exception as e:
        logger.error(f"Error loading index.html: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to load frontend"}), 500

@app.route('/convert', methods=['POST'])
def convert():
    """ Convert YouTube video to MP3 and upload it """
    try:
        data = request.get_json()
        youtube_url = data.get("youtube_url")

        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        logger.info(f"Processing download request for URL: {youtube_url}")
        output_file = download_audio(youtube_url, DOWNLOAD_FOLDER)

        if not output_file:
            logger.error("Failed to download video.")
            return jsonify({"error": "Failed to download and convert video"}), 500

        # ✅ Upload to Supabase Storage
        logger.info("Uploading to Supabase Storage...")
        storage = StorageUploader()
        public_url = storage.upload_file(output_file)

        if not public_url:
            logger.error("Failed to upload file to storage.")
            return jsonify({"error": "Failed to upload file to storage"}), 500

        # ✅ Store record in database
        insert_success = insert_download_record(youtube_url, output_file, public_url)
        if not insert_success:
            logger.warning("Failed to insert download record into database.")

        return jsonify({
            "success": True,
            "file_path": output_file,
            "mp3_url": public_url
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    # ✅ Ensure it runs on port 5000 for Railway deployment
    app.run(host='0.0.0.0', port=5000, debug=True)
