import os
import logging
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vakalat.log"),
        logging.StreamHandler()
    ]
)

def create_temp_file(extension: str) -> str:
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
        temp_path = temp_file.name
        temp_file.close()
        logging.info(f"Created temporary file: {temp_path}")
        return temp_path
    except Exception as e:
        logging.error(f"Error creating temporary file: {e}")
        return None

def save_uploaded_file(file) -> str:
    if not file:
        logging.error("No file provided")
        return None

    logging.info(f"Processing file: {file}, type: {type(file)}, attributes: {dir(file)}")
    
    # Reject invalid types
    if isinstance(file, (int, float)):
        logging.error(f"Invalid file type: {type(file)}")
        return None

    try:
        # Handle Gradio NamedString or file-like objects
        if isinstance(file, str):
            # If file is a string path, extract extension from the path itself
            extension = Path(file).suffix or '.tmp'
        else:
            # For file-like objects, use the name attribute
            file_name = getattr(file, 'name', 'uploaded_file')
            extension = Path(file_name).suffix or '.tmp'
        temp_path = create_temp_file(extension)
        
        if not temp_path:
            logging.error("Failed to create temporary file")
            return None

        # Check if file has a read method (file-like object)
        if hasattr(file, 'read'):
            content = file.read()
        else:
            # Handle string path or NamedString content
            logging.info("File lacks 'read' method, handling as NamedString or similar")
            logging.info(f"Initial content type: {type(file)}")
            
            # If file is a string (path or content), assume it's a path or convert to bytes
            if isinstance(file, str):
                if os.path.exists(file):
                    with open(file, 'rb') as f:
                        content = f.read()
                else:
                    content = file.encode('utf-8')
            else:
                content = str(file).encode('utf-8')

        logging.info("Converting string content to bytes")

        # Validate PDF content
        if extension.lower() == '.pdf':
            if not content.startswith(b'%PDF'):
                logging.error("Invalid PDF content: Missing %PDF header")
                return None

        # Validate audio file
        valid_audio_exts = {'.flac', '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.ogg', '.opus', '.wav', '.webm'}
        if extension.lower() in valid_audio_exts:
            if not content:  # Check for empty content
                logging.error("Invalid audio content: Empty file")
                return None
            # Basic audio file header check (example for WAV)
            if extension.lower() == '.wav' and not content.startswith(b'RIFF'):
                logging.error("Invalid WAV file: Missing RIFF header")
                return None

        # Write content to temporary file
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        logging.info(f"Saved uploaded file to {temp_path}")
        return temp_path

    except Exception as e:
        logging.error(f"Error saving file {file_name}: {e}")
        return None

def cleanup_temp_files(temp_files: list) -> None:
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logging.info(f"Deleted temporary file: {file_path}")
        except Exception as e:
            logging.error(f"Error deleting temporary file {file_path}: {e}")

def save_text_to_file(text: str, extension: str, prefix: str = "output") -> str:
    try:
        temp_path = create_temp_file(extension)
        if not temp_path:
            logging.error("Failed to create temporary file for text")
            return None
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logging.info(f"Saved text to file: {temp_path}")
        return temp_path
    except Exception as e:
        logging.error(f"Error saving text to file: {e}")
        return None