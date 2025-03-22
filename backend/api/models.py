from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Article(BaseModel):
    title: str
    summary: str
    sentiment: str
    topics: List[str]
    source: str
    url: str
    published_date: Optional[datetime] = None

class SentimentDistribution(BaseModel):
    positive: int = Field(default=0)
    negative: int = Field(default=0)
    neutral: int = Field(default=0)

class CoverageDifference(BaseModel):
    comparison: str
    impact: str

class TopicOverlap(BaseModel):
    common_topics: List[str]
    unique_topics: Dict[str, List[str]]

class ComparativeAnalysis(BaseModel):
    sentiment_distribution: SentimentDistribution
    coverage_differences: List[CoverageDifference]
    topic_overlap: TopicOverlap

class AnalysisResponse(BaseModel):
    company: str
    articles: List[Article]
    comparative_analysis: ComparativeAnalysis
    final_sentiment: str
    audio_url: Optional[str] = None

class CompanyRequest(BaseModel):
    company_name: str = Field(..., description="Name of the company to analyze")

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language: str = Field(default="hi", description="Language code for TTS")

class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    language: str 