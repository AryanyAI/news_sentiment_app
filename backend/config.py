from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "News Sentiment Analysis"
    
    # News API Settings
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    
    # Model Settings
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    SENTIMENT_MODEL: str = "nlptown/bert-base-multilingual-uncased-sentiment"
    
    # Scraping Settings
    MAX_ARTICLES: int = 10
    REQUEST_TIMEOUT: int = 30
    
    # TTS Settings
    TTS_LANGUAGE: str = "hi"
    TTS_SPEED: float = 1.0
    
    # Cache Settings
    CACHE_TTL: int = 3600  # 1 hour
    
    # News Sources
    NEWS_SOURCES: List[str] = [
        "reuters.com",
        "bloomberg.com",
        "economictimes.indiatimes.com",
        "moneycontrol.com",
        "livemint.com"
    ]
    
    class Config:
        case_sensitive = True

settings = Settings()