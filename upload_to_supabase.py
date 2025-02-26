import os
import sys
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ygvjfdpruwsotbimdjch.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlndmpmZHBydXdzb3RiaW1kamNoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA1MzYxNDIsImV4cCI6MjA1NjExMjE0Mn0.oeTfCg_zZrOnepRRQXvukpWSyRrj1nJHSY637hJuy8o"
BUCKET_NAME = "audio"

def upload_to_supabase(file_path):
    """
    Upload file to Supabase Storage

    Args:
        file_path (str): Path to the file to upload

    Returns:
        dict: Response from Supabase Storage API
    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None

        filename = os.path.basename(file_path)
        logger.info(f"Uploading file: {filename}")

        with open(file_path, "rb") as f:
            response = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{filename}",
                headers={
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Cache-Control": "3600",
                    "Content-Type": "audio/mpeg"
                },
                data=f
            )

        if response.status_code == 200:
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{filename}"
            logger.info(f"File uploaded successfully. Public URL: {public_url}")
            return {"success": True, "url": public_url}
        else:
            logger.error(f"Upload failed with status code {response.status_code}: {response.text}")
            return {"success": False, "error": response.text}

    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        return {"success": False, "error": str(e)}

# Test the uploader if run directly
if __name__ == "__main__":
    # Use command line argument if provided, otherwise use default file
    mp3_file = sys.argv[1] if len(sys.argv) > 1 else "What_is_Prompt_Engineering_in_about_a_minute.mp3"
    
    if os.path.exists(mp3_file):
        response = upload_to_supabase(mp3_file)
        print(f"Upload result: {response}")
    else:
        print(f"Error: File not found: {mp3_file}")
        sys.exit(1)