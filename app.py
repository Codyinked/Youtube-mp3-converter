from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import logging
from youtube_audio_downloader import process_download
from database import insert_download_record
from storage import StorageUploader

# ✅ Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize Flask app & CORS
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ Ensure downloads directory exists
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    """ Serve the frontend HTML file """
    return send_from_directory("static", "index.html")

@app.route("/convert", methods=["POST"])
def convert():
    """ Convert YouTube video to MP3 and upload it """
    try:
        data = request.get_json()
        youtube_url = data.get("youtube_url")

        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        logger.info(f"Processing download request for URL: {youtube_url}")
        output_file = process_download(youtube_url, DOWNLOAD_FOLDER)

        if not output_file:
            logger.error("Failed to download video.")
            return jsonify({"error": "Failed to download and convert video"}), 500

        return jsonify({
            "success": True,
            "file_path": output_file,
            "mp3_url": f"/downloads/{os.path.basename(output_file)}"
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

