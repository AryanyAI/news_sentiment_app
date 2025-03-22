from gtts import gTTS
import os
import logging
from typing import Optional
from config import settings
import uuid
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.output_dir = "static/audio"
        self._ensure_output_dir()
        self.logger = logging.getLogger(__name__)

    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def generate_audio(self, text: str, language: str = "hi") -> str:
        """
        Generate audio file from text using gTTS
        """
        try:
            self.logger.info(f"Generating audio for text of length {len(text)} in language '{language}'")
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Ensure text is not empty
            if not text or len(text.strip()) == 0:
                text = "No text was provided for conversion to speech."
                self.logger.warning("Empty text provided for TTS, using default message")
            
            # If Hindi text, ensure it's correctly encoded
            if language == "hi":
                # Add some basic Hindi greeting to ensure we're testing Hindi capabilities
                hindi_greeting = "नमस्ते, "
                if not any(ord(c) > 127 for c in text):  # No Unicode chars, likely not Hindi
                    self.logger.warning("Hindi language selected but text might not be in Hindi")
                    text = hindi_greeting + text  # Prepend greeting to ensure some Hindi content
            
            # Generate speech
            self.logger.info("Calling gTTS to generate audio")
            tts = gTTS(text=text, lang=language, slow=False)
            
            self.logger.info(f"Saving audio to file: {filepath}")
            tts.save(filepath)
            
            # Log success and file size
            file_size = os.path.getsize(filepath)
            self.logger.info(f"Successfully generated audio file of size {file_size} bytes")
            
            # Return URL
            url = f"http://localhost:8000/static/audio/{filename}"
            self.logger.info(f"Audio URL: {url}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            # Create a fallback audio file with error message
            try:
                fallback_filename = f"error_{uuid.uuid4()}.mp3"
                fallback_filepath = os.path.join(self.output_dir, fallback_filename)
                
                # Generate fallback audio in English
                fallback_tts = gTTS(
                    text="Sorry, there was an error generating the audio. Please try again later.",
                    lang="en",
                    slow=False
                )
                fallback_tts.save(fallback_filepath)
                return f"http://localhost:8000/static/audio/{fallback_filename}"
            except Exception as nested_error:
                self.logger.error(f"Failed to create fallback audio: {str(nested_error)}")
                raise e  # Re-raise the original error if fallback fails

    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up old audio files
        """
        try:
            current_time = datetime.now()
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # Calculate age in hours
                age_hours = (current_time - file_modified).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    os.remove(filepath)
                    self.logger.info(f"Deleted old audio file: {filename}")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up old files: {str(e)}")

    def get_audio_duration(self, filepath: str) -> Optional[float]:
        """
        Get duration of audio file in seconds
        """
        try:
            # This is a placeholder - implement actual audio duration calculation
            # You might want to use a library like mutagen or pydub
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {str(e)}")
            return None 