from gtts import gTTS
import os
import logging
from typing import Optional
from config import settings
import uuid
from datetime import datetime
from deep_translator import GoogleTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        self.output_dir = "static/audio"
        self._ensure_output_dir()
        self.logger = logging.getLogger(__name__)
        self.translator = GoogleTranslator(source='en', target='hi')

    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    async def generate_audio(self, text: str, language: str = "hi") -> str:
        """
        Generate audio file from text using gTTS
        """
        try:
            self.logger.info(f"Generating audio for text of length {len(text)}")
            
            # Generate unique filename
            filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Ensure text is not empty
            if not text or len(text.strip()) == 0:
                text = "कोई टेक्स्ट प्रदान नहीं किया गया है।"
                self.logger.warning("Empty text provided for TTS, using default message")
            
            # Translate text to Hindi if not already in Hindi
            if language == "hi" and not any(ord(c) > 127 for c in text):
                self.logger.info("Text appears to be in English, translating to Hindi")
                try:
                    hindi_text = self.translator.translate(text)
                    if hindi_text and any(ord(c) > 127 for c in hindi_text):
                        self.logger.info("Translation successful")
                        text = hindi_text
                    else:
                        self.logger.warning("Translation didn't produce Hindi text, using original with prefix")
                        text = "अनुवाद असफल होने के बाद मूल संदेश: " + text
                except Exception as e:
                    self.logger.error(f"Translation error: {str(e)}")
                    text = "अनुवाद त्रुटि के बाद मूल संदेश: " + text
            
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
            # Create fallback audio
            fallback_text = "क्षमा करें, ऑडियो जनरेट करने में त्रुटि हुई है।"
            fallback_filename = f"error_{uuid.uuid4()}.mp3"
            fallback_path = os.path.join(self.output_dir, fallback_filename)
            try:
                fallback_tts = gTTS(text=fallback_text, lang="hi")
                fallback_tts.save(fallback_path)
                return f"http://localhost:8000/static/audio/{fallback_filename}"
            except:
                raise e

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