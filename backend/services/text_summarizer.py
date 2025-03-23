from transformers import pipeline
from typing import List
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextSummarizer:
    def __init__(self):
        self.model_name = settings.SUMMARIZATION_MODEL
        try:
            self.summarizer = pipeline(
                "summarization",
                model=self.model_name,
                device=-1  # Use CPU
            )
            logger.info(f"Initialized summarizer with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing summarizer: {str(e)}")
            raise

    async def summarize(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """
        Generate a summary of the input text
        """
        try:
            # Ensure text is not empty
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided for summarization")
                return "No content available for summarization."
            
            # Split text into chunks if it's too long
            chunks = self._split_text(text)
            
            if not chunks:
                return "Content too short to summarize."
            
            logger.info(f"Split text into {len(chunks)} chunks for summarization")
            
            summaries = []
            for i, chunk in enumerate(chunks):
                # Dynamically adjust max_length based on input length
                input_length = len(chunk.split())
                
                # Ensure we're generating a reasonable summary size (1/3 to 1/2 of text)
                adjusted_max_length = min(max_length, max(min_length, input_length // 2))
                adjusted_min_length = min(min_length, max(30, input_length // 4))
                
                logger.info(f"Summarizing chunk {i+1}/{len(chunks)} with max_length={adjusted_max_length}, min_length={adjusted_min_length}")
                
                try:
                    summary = self.summarizer(
                        chunk,
                        max_length=adjusted_max_length,
                        min_length=adjusted_min_length,
                        do_sample=False
                    )[0]['summary_text']
                    summaries.append(summary)
                    logger.info(f"Generated summary for chunk {i+1} of length {len(summary.split())} words")
                except Exception as e:
                    logger.error(f"Error in summarization chunk {i+1}: {str(e)}")
                    # Fallback summary - extract first 2-3 sentences
                    sentences = chunk.split('.')[:3]
                    fallback_summary = '. '.join(sentences) + '.'
                    summaries.append(fallback_summary)
                    logger.info(f"Using fallback summary for chunk {i+1}")
            
            # Combine summaries if there were multiple chunks
            final_summary = " ".join(summaries)
            
            # If the combined summary is too long, generate a meta-summary
            if len(summaries) > 1 and len(final_summary.split()) > max_length:
                logger.info("Combined summary too long, generating meta-summary")
                try:
                    final_summary = self.summarizer(
                        final_summary,
                        max_length=max_length,
                        min_length=min_length,
                        do_sample=False
                    )[0]['summary_text']
                    logger.info(f"Generated meta-summary of length {len(final_summary.split())} words")
                except Exception as e:
                    logger.error(f"Error in meta-summarization: {str(e)}")
                    # If meta-summarization fails, just truncate with ellipsis
                    words = final_summary.split()
                    if len(words) > max_length:
                        final_summary = ' '.join(words[:max_length]) + '...'
            
            return final_summary
                
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            # More robust fallback - return first paragraph or sentences
            sentences = text.split('.')[:5]  # First 5 sentences
            return '. '.join(sentences) + '.'

    async def extract_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """Extract more specific and accurate topics from text"""
        try:
            # Convert to lowercase for easier matching
            text_lower = text.lower()
            
            # Find company-specific topics based on content
            company_topics = {
                "microsoft": ["windows", "office", "teams", "skype", "azure", "onenote", 
                             "365", "satya nadella", "bill gates", "copilot", "surface", 
                             "xbox", "directx", "bing", "edge", "visual studio"],
                "tesla": ["electric vehicles", "elon musk", "model 3", "autopilot", 
                         "battery", "solar", "cybertruck", "gigafactory", "supercharger"],
                "apple": ["iphone", "ipad", "mac", "ios", "macos", "macbook", "airpods", 
                         "app store", "tim cook", "watch", "siri", "itunes", "safari"],
                "google": ["search", "android", "chrome", "gmail", "youtube", "workspace", 
                          "cloud", "pixel", "maps", "assistant", "alphabet", "sundar pichai"],
                "amazon": ["e-commerce", "aws", "alexa", "prime", "jeff bezos", "kindle", 
                          "marketplace", "web services", "warehouse", "logistics"]
            }
            
            # Find company name in text to determine which specific terms to look for
            company_name = None
            for company in company_topics.keys():
                if company in text_lower:
                    company_name = company
                    break
            
            # Get company-specific terms
            specific_terms = []
            if company_name:
                specific_terms = company_topics[company_name]
            
            # Match specific company terms in content
            matched_topics = []
            for term in specific_terms:
                if term in text_lower:
                    matched_topics.append(term)
            
            # General industry topics
            industry_topics = {
                "finance": ["earnings", "revenue", "profit", "stock", "investors", "market", 
                           "growth", "dividend", "financial", "quarterly", "fiscal"],
                "technology": ["software", "hardware", "app", "device", "digital", "innovation", 
                              "product", "development", "design", "features", "technology"],
                "regulation": ["compliance", "investigation", "regulatory", "legal", "scrutiny", 
                              "regulation", "lawsuit", "settlement", "allegation", "violation"],
                "business": ["strategy", "growth", "performance", "expansion", "competition", 
                            "leadership", "executive", "CEO", "management", "restructuring"],
                "security": ["malware", "hacking", "vulnerability", "patch", "security", 
                            "protection", "threat", "attack", "defense", "safeguard"]
            }
            
            # Check which topics are mentioned in the text
            topic_matches = {}
            
            for category, terms in industry_topics.items():
                for term in terms:
                    if term in text_lower and len(term) > 3:  # Avoid short generic terms
                        if term not in topic_matches:
                            topic_matches[term] = 1
                        else:
                            topic_matches[term] += 1
            
            # Add specific topics first (limit to 3)
            found_topics = matched_topics[:3]
            
            # Add general topics next
            sorted_topics = sorted(topic_matches.items(), key=lambda x: x[1], reverse=True)
            for topic, count in sorted_topics:
                if topic not in found_topics and len(found_topics) < max_topics:
                    found_topics.append(topic)
            
            # If we still don't have enough topics, add some generic ones
            if len(found_topics) < 3:
                generic_topics = ["business", "market", "industry", "company", "news", "update"]
                for topic in generic_topics:
                    if topic not in found_topics and len(found_topics) < max_topics:
                        found_topics.append(topic)
            
            return found_topics[:max_topics]
            
        except Exception as e:
            logger.error(f"Error extracting topics: {str(e)}")
            return ["business", "news", "update"]

    def _split_text(self, text: str, max_chunk_length: int = 1024) -> List[str]:
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