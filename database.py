import os
import psycopg2
from urllib.parse import urlparse
import logging
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Establish a connection to PostgreSQL using the DATABASE_URL"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in environment variables")

    try:
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def insert_download_record(video_id: str, title: str, file_path: str, public_url: str = None) -> bool:
    """
    Insert a record of downloaded video into the database
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
        return False

def get_download_history() -> list:
    """
    Get list of all downloaded videos
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
