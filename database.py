import os
import psycopg2
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        logger.info("Attempting to connect to database...")
        conn = psycopg2.connect(
            host=os.environ.get("PGHOST"),
            database=os.environ.get("PGDATABASE"),
            user=os.environ.get("PGUSER"),
            password=os.environ.get("PGPASSWORD"),
            port=os.environ.get("PGPORT")
        )
        logger.info("Successfully connected to database")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def insert_download_record(video_id: str, title: str, file_path: str, public_url: str = None) -> bool:
    """
    Insert a record of downloaded video into the database

    Args:
        video_id (str): YouTube video ID
        title (str): Video title
        file_path (str): Path to the downloaded MP3 file
        public_url (str, optional): Public URL of the uploaded file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Attempting to insert download record for video ID: {video_id}")
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                logger.info("Executing INSERT statement...")
                cur.execute(
                    """
                    INSERT INTO downloads (video_id, title, file_path, downloaded_at, public_url)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (video_id, title, file_path, datetime.utcnow(), public_url)
                )
                record_id = cur.fetchone()[0]
                conn.commit()
                logger.info(f"Successfully recorded download for video: {title} (ID: {record_id})")
                return True

    except Exception as e:
        logger.error(f"Error recording download: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        return False

def get_download_history() -> list:
    """
    Get list of all downloaded videos

    Returns:
        list: List of downloaded video records
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT video_id, title, file_path, downloaded_at
                    FROM downloads
                    ORDER BY downloaded_at DESC
                    """
                )
                return cur.fetchall()
    except Exception as e:
        logger.error(f"Error fetching download history: {str(e)}")
        return []