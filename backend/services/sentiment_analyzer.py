from transformers import pipeline
from typing import List, Dict
import logging
from config import settings
from api.models import SentimentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = settings.SENTIMENT_MODEL
        try:
            self.analyzer = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=-1  # Use CPU
            )
            logger.info(f"Initialized sentiment analyzer with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {str(e)}")
            raise

    async def analyze(self, text: str) -> str:
        """
        Analyze sentiment of the input text
        """
        try:
            # Split text into chunks if it's too long
            chunks = self._split_text(text)
            
            # Analyze each chunk
            sentiments = []
            for chunk in chunks:
                try:
                    result = self.analyzer(chunk)[0]
                    sentiments.append(result)
                except Exception as e:
                    logger.error(f"Error in chunk sentiment analysis: {str(e)}")
                    # Fallback when model fails
                    sentiments.append({"label": "NEUTRAL", "score": 0.5})
            
            # Aggregate sentiments
            return self._aggregate_sentiments(sentiments)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return "neutral"

    async def generate_final_sentiment(self, articles: List[Dict]) -> str:
        """
        Generate a final sentiment summary from multiple articles
        """
        try:
            # Check if there are any articles
            if not articles:
                return "No articles were found for analysis."
            
            # Count sentiment distribution
            sentiment_counts = {
                "positive": 0,
                "negative": 0,
                "neutral": 0
            }
            
            for article in articles:
                sentiment = article.get("sentiment", "neutral")
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1
            
            # Generate summary based on distribution
            total_articles = len(articles)
            positive_ratio = sentiment_counts["positive"] / total_articles
            negative_ratio = sentiment_counts["negative"] / total_articles
            
            if positive_ratio > 0.6:
                return f"{articles[0]['title'].split()[0]}'s latest news coverage is strongly positive. {sentiment_counts['positive']} out of {total_articles} articles show positive sentiment, indicating favorable market perception."
            elif positive_ratio > 0.4:
                return f"{articles[0]['title'].split()[0]}'s latest news coverage is generally positive. {sentiment_counts['positive']} out of {total_articles} articles show positive sentiment, with some neutral coverage."
            elif negative_ratio > 0.6:
                return f"{articles[0]['title'].split()[0]}'s latest news coverage is predominantly negative. {sentiment_counts['negative']} out of {total_articles} articles show negative sentiment, which may impact investor confidence."
            elif negative_ratio > 0.4:
                return f"{articles[0]['title'].split()[0]}'s latest news coverage shows concerning trends. {sentiment_counts['negative']} out of {total_articles} articles show negative sentiment, though some positive aspects were noted."
            else:
                return f"{articles[0]['title'].split()[0]}'s latest news coverage is mixed, with balanced positive and negative reporting. Most coverage ({sentiment_counts['neutral']} articles) maintains a neutral stance."
                
        except Exception as e:
            logger.error(f"Error generating final sentiment: {str(e)}")
            return "Unable to generate final sentiment summary."

    def _aggregate_sentiments(self, sentiments: List[Dict]) -> str:
        """
        Aggregate sentiment scores from multiple chunks
        """
        try:
            # Check if we have model results
            if all("label" in sentiment for sentiment in sentiments):
                # Using real model results
                scores = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
                for sentiment in sentiments:
                    label = sentiment["label"]
                    if label in scores:
                        scores[label] += 1
                
                max_label = max(scores, key=scores.get)
                if max_label == "POSITIVE":
                    return "positive"
                elif max_label == "NEGATIVE":
                    return "negative"
                else:
                    return "neutral"
            else:
                # Fallback approach with keyword matching for mock data
                text = " ".join([sentiment.get("text", "") for sentiment in sentiments])
                text = text.lower()
                
                # Check for positive keywords
                positive_keywords = ["above expectations", "growth", "strong performance", 
                                    "positive", "upgrade", "rose", "increase", "innovation",
                                    "success", "profit", "confidence", "surge"]
                
                # Check for negative keywords
                negative_keywords = ["below expectations", "decline", "poor performance", 
                                    "negative", "downgrade", "fell", "decrease", "scrutiny", 
                                    "investigation", "complaint", "concern", "risk", "failure"]
                
                # Count keyword occurrences
                positive_count = sum(1 for keyword in positive_keywords if keyword in text)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text)
                
                # Determine sentiment
                if positive_count > negative_count + 1:  # Give some preference to positive
                    return "positive"
                elif negative_count > 0:  # Be more sensitive to negative sentiment
                    return "negative"
                else:
                    return "neutral"
                
        except Exception as e:
            logger.error(f"Error aggregating sentiments: {str(e)}")
            return "neutral"

    def _split_text(self, text: str, max_chunk_length: int = 512) -> List[str]:
        """
        Split text into chunks that fit within the model's context window
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            if current_length >= max_chunk_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks 