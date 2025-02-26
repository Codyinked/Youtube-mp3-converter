import os
import re
from urllib.parse import urlparse, parse_qs

def validate_url(url):
    """
    Validate YouTube URL format
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    # YouTube URL patterns
    patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/v/[\w-]+',
        r'^https?://youtu\.be/[\w-]+',
        r'^https?://(?:www\.)?youtube\.com/embed/[\w-]+'
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False

def create_output_directory(directory):
    """
    Create output directory if it doesn't exist
    
    Args:
        directory (str): Directory path to create
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def sanitize_filename(filename):
    """
    Remove invalid characters from filename
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length to 255 characters
    filename = filename[:255]
    return filename
