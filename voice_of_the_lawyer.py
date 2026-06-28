from gtts import gTTS
import os
import logging
from utils import create_temp_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("vakalat.log"),
        logging.StreamHandler()
    ]
)

def speak_response(text: str) -> str:
    if not text:
        logging.error("No text provided for TTS")
        return None

    mp3_path = create_temp_file(".mp3")
    try:
        logging.info("Using gTTS for TTS")
        tts = gTTS(text=text, lang='en')
        tts.save(mp3_path)
        logging.info(f"TTS audio saved: {mp3_path}")
        return mp3_path
    except Exception as e:
        logging.error(f"Error generating TTS: {e}")
        return None