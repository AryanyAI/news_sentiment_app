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
        """Analyze sentiment with better negative text detection"""
        try:
            # Check for explicitly negative words first
            text_lower = text.lower()
            
            # Strong negative patterns that should override other analysis
            negative_phrases = [
                "killing", "malware", "abuse", "hack", "vulnerability", "attack", 
                "lawsuit", "scandal", "breach", "risk", "threat", "warning",
                "drastic", "axe", "duck", "question", "lack of consent", "politico"
            ]
            
            # Check for these phrases and immediately return negative if found
            for phrase in negative_phrases:
                if phrase in text_lower:
                    return "negative"
            
            # Split text for analysis if phrases not found
            chunks = self._split_text(text)
            
            # Analyze each chunk
            sentiments = []
            for chunk in chunks:
                try:
                    result = self.analyzer(chunk)[0]
                    sentiments.append(result)
                except Exception as e:
                    logger.error(f"Error in chunk sentiment analysis: {str(e)}")
                    # Fallback to keyword-based analysis for this chunk
                    sentiments.append(self._keyword_based_sentiment(chunk))
            
            # Aggregate sentiments
            return self._aggregate_sentiments(sentiments, text)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return self._keyword_based_sentiment(text)

    def _keyword_based_sentiment(self, text: str) -> Dict:
        """Analyze sentiment based on keywords"""
        text_lower = text.lower()
        
        negative_keywords = [
            "scrutiny", "investigation", "concern", "risk", "failure", "decline", 
            "violation", "regulatory", "allegations", "lawsuit", "probe", "issue", 
            "problem", "challenge", "fine", "penalty", "crisis", "fraud", "complaint",
            "criticism", "plunge", "crash", "disappointing", "disappointed", "troubles",
            "halt", "suspend", "struggle", "warning", "downgrade", "recall", "deficit"
        ]
        
        positive_keywords = [
            "growth", "profit", "successful", "launch", "innovation", "partnership",
            "expansion", "rise", "increase", "record", "exceed", "surpass", "positive",
            "improvement", "upgraded", "opportunity", "achievement", "breakthrough",
            "milestone", "award", "recognition", "excellent", "boost", "strong"
        ]
        
        negative_score = sum(1 for word in negative_keywords if word in text_lower)
        positive_score = sum(1 for word in positive_keywords if word in text_lower)
        
        if negative_score > positive_score:
            return {"label": "NEGATIVE", "score": 0.8}
        elif positive_score > negative_score:
            return {"label": "POSITIVE", "score": 0.8}
        else:
            return {"label": "NEUTRAL", "score": 0.5}

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
            
            # Get company name from request rather than article content
            # The issue is here - we need to get the actual company name
            company_name = articles[0].get('company', '')
            
            # Get company name from the API route
            if not company_name:
                # Extract from first article title if possible
                title = articles[0].get('title', '')
                words = title.split()
                # Try to find company name in title
                for word in words:
                    if word.lower() in ['microsoft', 'apple', 'tesla', 'google', 'amazon']:
                        company_name = word
                        break
                
                # Default if still not found
                if not company_name:
                    # Look at source parameter which often has company name
                    url_parts = articles[0].get('url', '').split('/')
                    for part in url_parts:
                        if part.lower() in ['microsoft', 'apple', 'tesla', 'google', 'amazon']:
                            company_name = part
                            break
                
                # Absolute fallback
                if not company_name:
                    company_name = "कंपनी" # Generic "company" in Hindi
            
            # Generate summary based on distribution
            total_articles = len(articles)
            positive_ratio = sentiment_counts["positive"] / total_articles
            negative_ratio = sentiment_counts["negative"] / total_articles
            neutral_ratio = sentiment_counts["neutral"] / total_articles
            
            if positive_ratio > 0.6:
                return f"{company_name} की हालिया समाचार कवरेज अत्यधिक सकारात्मक है। {sentiment_counts['positive']} में से {total_articles} लेख सकारात्मक भावना दिखाते हैं, जो बाजार की अनुकूल धारणा को इंगित करता है।"
            elif positive_ratio > 0.4:
                return f"{company_name} की हालिया समाचार कवरेज आम तौर पर सकारात्मक है। {sentiment_counts['positive']} में से {total_articles} लेख सकारात्मक भावना दिखाते हैं, कुछ तटस्थ कवरेज के साथ।"
            elif negative_ratio > 0.6:
                return f"{company_name} की हालिया समाचार कवरेज मुख्य रूप से नकारात्मक है। {sentiment_counts['negative']} में से {total_articles} लेख नकारात्मक भावना दिखाते हैं, जो निवेशक के विश्वास को प्रभावित कर सकता है।"
            elif negative_ratio > 0.4:
                return f"{company_name} की हालिया समाचार कवरेज चिंताजनक रुझान दिखाती है। {sentiment_counts['negative']} में से {total_articles} लेख नकारात्मक भावना दिखाते हैं, हालांकि कुछ सकारात्मक पहलुओं पर भी ध्यान दिया गया है।"
            elif neutral_ratio > 0.6:
                return f"{company_name} की हालिया समाचार कवरेज मुख्य रूप से तटस्थ है। {sentiment_counts['neutral']} में से {total_articles} लेख तटस्थ दृष्टिकोण बनाए रखते हैं।"
            else:
                return f"{company_name} की हालिया समाचार कवरेज मिश्रित है, सकारात्मक और नकारात्मक रिपोर्टिंग के बीच संतुलन के साथ। अधिकांश कवरेज ({sentiment_counts['neutral']} लेख) तटस्थ रुख रखती है।"
                
        except Exception as e:
            logger.error(f"Error generating final sentiment: {str(e)}")
            return "समाचार विश्लेषण में त्रुटि हुई। कृपया बाद में पुन: प्रयास करें।"

    def _aggregate_sentiments(self, sentiments: List[Dict], full_text: str) -> str:
        """
        Aggregate sentiment scores with better negative and neutral detection
        """
        try:
            # Count sentiment labels
            label_counts = {"POSITIVE": 0, "NEGATIVE": 0, "NEUTRAL": 0}
            
            for sentiment in sentiments:
                label = sentiment.get("label", "NEUTRAL")
                if label in label_counts:
                    score = sentiment.get("score", 0.5)
                    label_counts[label] += score
            
            # Give negative content more weight
            text_lower = full_text.lower()
            
            # Look for stronger negative phrases
            negative_phrases = [
                "regulatory scrutiny", "investigation", "lawsuit", "probe", 
                "violation", "concerns", "issues", "penalty", "fine", "scandal",
                "crisis", "downgrade", "underperform", "warning", "debt", 
                "sabotage", "jail", "prison", "fraud", "protest", "vandalism"
            ]
            
            # Look for neutral indicators
            neutral_phrases = [
                "announced", "unveiled", "revealed", "reported", "stated", 
                "said", "according to", "podcast", "interview", "meeting"
            ]
            
            # Apply stronger weights to negative content
            for phrase in negative_phrases:
                if phrase in text_lower:
                    label_counts["NEGATIVE"] += 1.5  # Higher weight for negative content
            
            # Apply neutral bias for news-reporting language
            for phrase in neutral_phrases:
                if phrase in text_lower and "exceed" not in text_lower and "growth" not in text_lower:
                    label_counts["NEUTRAL"] += 0.5
            
            # Determine final sentiment with a slight negative bias
            if label_counts["NEGATIVE"] > 0:
                label_counts["NEGATIVE"] *= 1.2  # 20% boost to negative sentiment
            
            max_label = max(label_counts, key=label_counts.get)
            
            if max_label == "POSITIVE":
                return "positive"
            elif max_label == "NEGATIVE":
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