from fastapi import APIRouter, HTTPException, Depends
from typing import List
from .models import (
    AnalysisResponse,
    CompanyRequest,
    TTSRequest,
    TTSResponse
)
from services.news_scraper import NewsScraper
from services.text_summarizer import TextSummarizer
from services.sentiment_analyzer import SentimentAnalyzer
from services.comparative_analysis import ComparativeAnalyzer
from services.tts_service import TTSService
from config import settings
import logging

router = APIRouter()

# Initialize services
news_scraper = NewsScraper()
text_summarizer = TextSummarizer()
sentiment_analyzer = SentimentAnalyzer()
comparative_analyzer = ComparativeAnalyzer()
tts_service = TTSService()

logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: CompanyRequest):
    """
    Analyze news articles for a given company
    """
    try:
        company_name = request.company_name
        logger.info(f"Analyzing company: {company_name}")
        
        # Get news articles
        logger.info("Fetching news articles...")
        articles = await news_scraper.get_articles(company_name)
        logger.info(f"Retrieved {len(articles)} articles")
        
        # Process each article
        processed_articles = []
        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}/{len(articles)}: {article['title'][:30]}...")
            
            # Add company field to each article
            article['company'] = company_name
            
            # Summarize article
            logger.info(f"Summarizing article {i+1}...")
            summary = await text_summarizer.summarize(article["content"])
            
            # Analyze sentiment
            logger.info(f"Analyzing sentiment for article {i+1}...")
            sentiment = await sentiment_analyzer.analyze(article["content"])
            logger.info(f"Sentiment for article {i+1}: {sentiment}")
            
            # Extract topics
            logger.info(f"Extracting topics for article {i+1}...")
            topics = await text_summarizer.extract_topics(article["content"])
            
            processed_articles.append({
                "title": article["title"],
                "summary": summary,
                "sentiment": sentiment,
                "topics": topics,
                "source": article["source"],
                "url": article["url"],
                "published_date": article.get("published_date"),
                "company": company_name  # Add company name to each processed article
            })
        
        # Perform comparative analysis
        logger.info("Performing comparative analysis...")
        comparative_analysis = await comparative_analyzer.analyze(processed_articles)
        
        # Generate final sentiment
        logger.info("Generating final sentiment...")
        final_sentiment = await sentiment_analyzer.generate_final_sentiment(processed_articles)
        
        # Generate TTS
        logger.info("Generating Hindi TTS audio...")
        audio_url = await tts_service.generate_audio(final_sentiment)
        logger.info(f"Generated audio at: {audio_url}")
        
        # Return final response
        logger.info("Analysis complete, returning response")
        return {
            "company": company_name,
            "articles": processed_articles,
            "comparative_analysis": comparative_analysis,
            "final_sentiment": final_sentiment,
            "audio_url": audio_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts", response_model=TTSResponse)
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    """
    try:
        audio_url = await tts_service.generate_audio(
            request.text,
            language=request.language
        )
        return {
            "audio_url": audio_url,
            "duration": 0.0,  # TODO: Implement duration calculation
            "language": request.language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 