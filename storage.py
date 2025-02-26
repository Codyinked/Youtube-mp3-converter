import os
import requests
import logging
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StorageUploader:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.bucket_name = "audio"
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing Supabase credentials in environment variables")

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to Supabase Storage
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            Optional[str]: Public URL of the uploaded file if successful, None otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None

            filename = os.path.basename(file_path)
            logger.info(f"Uploading file: {filename} to Supabase Storage")

            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}",
                    headers={
                        "Authorization": f"Bearer {self.supabase_key}",
                        "Cache-Control": "3600",
                        "Content-Type": "audio/mpeg"
                    },
                    data=f
                )

            if response.status_code == 200:
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
                logger.info(f"File uploaded successfully. Public URL: {public_url}")
                return public_url
            else:
                logger.error(f"Upload failed with status code {response.status_code}: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                logger.error(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
            return None

# Test the uploader if run directly
if __name__ == "__main__":
    test_file = "What_is_Prompt_Engineering_in_about_a_minute.mp3"
    if os.path.exists(test_file):
        uploader = StorageUploader()
        result = uploader.upload_file(test_file)
        print(f"Upload result: {result}")
    else:
        print(f"Test file not found: {test_file}")
