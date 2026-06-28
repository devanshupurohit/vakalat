import os
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from dotenv import load_dotenv
from groq import Groq
from utils import create_temp_file, cleanup_temp_files

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

def record_audio(timeout: int = 20, phrase_time_limit: int = 30) -> str:
    recognizer = sr.Recognizer()
    file_path = create_temp_file(".mp3")
    
    try:
        with sr.Microphone() as source:
            logging.info("Adjusting for background noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            logging.info("Please describe your legal problem clearly...")
            
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            logging.info("Recording complete.")
            
            wav_data = audio_data.get_wav_data()
            audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
            audio_segment.export(file_path, format="mp3", bitrate="128k")
            
            logging.info(f"Voice recording saved to {file_path}")
            return file_path
    except Exception as e:
        logging.error(f"Recording failed: {e}")
        return None

def convert_mp3_to_wav(mp3_path: str) -> str:
    wav_path = create_temp_file(".wav")
    try:
        audio = AudioSegment.from_mp3(mp3_path)
        audio.export(wav_path, format="wav")
        logging.info(f"Converted MP3 to WAV: {wav_path}")
        return wav_path
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return None

def transcribe_with_groq(stt_model: str, audio_filepath: str) -> str:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=stt_model,
                file=audio_file,
                language="en"
            )
            logging.info(f"Transcription Result: {transcription.text}")
            return transcription.text
    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return None

def transcribe_audio(audio_filepath: str, stt_model: str = "whisper-large-v3") -> str:
    try:
        wav_path = audio_filepath
        if audio_filepath.lower().endswith(".mp3"):
            wav_path = convert_mp3_to_wav(audio_filepath)
            if not wav_path:
                return None
        
        transcription = transcribe_with_groq(stt_model, wav_path)
        
        if wav_path != audio_filepath:
            os.remove(wav_path)
            logging.info(f"Cleaned up temporary WAV file: {wav_path}")
        
        return transcription
    except Exception as e:
        logging.error(f"transcribe_audio error: {e}")
        return None

def main():
    recorded = record_audio()
    if recorded:
        result = transcribe_audio(recorded)
        if result:
            print("\n🗣️ Transcribed Legal Query:\n", result)
        cleanup_temp_files(["*.mp3", "*.wav"])

if __name__ == "__main__":
    main()