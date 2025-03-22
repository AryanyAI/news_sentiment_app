from typing import List, Dict, Set
import logging
from collections import Counter
from api.models import (
    SentimentDistribution,
    CoverageDifference,
    TopicOverlap,
    ComparativeAnalysis
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComparativeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def analyze(self, articles: List[Dict]) -> ComparativeAnalysis:
        """
        Perform comparative analysis on a list of articles
        """
        try:
            # Calculate sentiment distribution
            sentiment_distribution = self._calculate_sentiment_distribution(articles)
            
            # Analyze coverage differences
            coverage_differences = self._analyze_coverage_differences(articles)
            
            # Analyze topic overlap
            topic_overlap = self._analyze_topic_overlap(articles)
            
            return ComparativeAnalysis(
                sentiment_distribution=sentiment_distribution,
                coverage_differences=coverage_differences,
                topic_overlap=topic_overlap
            )
            
        except Exception as e:
            self.logger.error(f"Error in comparative analysis: {str(e)}")
            raise

    def _calculate_sentiment_distribution(self, articles: List[Dict]) -> SentimentDistribution:
        """
        Calculate the distribution of sentiments across articles
        """
        try:
            sentiment_counts = Counter(article["sentiment"] for article in articles)
            
            return SentimentDistribution(
                positive=sentiment_counts.get("positive", 0),
                negative=sentiment_counts.get("negative", 0),
                neutral=sentiment_counts.get("neutral", 0)
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment distribution: {str(e)}")
            return SentimentDistribution()

    def _analyze_coverage_differences(self, articles: List[Dict]) -> List[CoverageDifference]:
        """
        Analyze differences in how articles cover the same topic
        """
        try:
            differences = []
            
            # Compare each article with others
            for i, article1 in enumerate(articles):
                for article2 in articles[i+1:]:
                    # Compare sentiment differences
                    if article1["sentiment"] != article2["sentiment"]:
                        differences.append(
                            CoverageDifference(
                                comparison=f"Article from {article1['source']} shows {article1['sentiment']} sentiment while {article2['source']} shows {article2['sentiment']} sentiment.",
                                impact=self._generate_impact_statement(article1["sentiment"], article2["sentiment"])
                            )
                        )
                    
                    # Compare topic differences
                    topic_diff = set(article1["topics"]) - set(article2["topics"])
                    if topic_diff:
                        differences.append(
                            CoverageDifference(
                                comparison=f"Article from {article1['source']} focuses on {', '.join(topic_diff)} while {article2['source']} does not cover these topics.",
                                impact=f"This difference in coverage suggests varying editorial priorities between sources."
                            )
                        )
            
            return differences
            
        except Exception as e:
            self.logger.error(f"Error analyzing coverage differences: {str(e)}")
            return []

    def _analyze_topic_overlap(self, articles: List[Dict]) -> TopicOverlap:
        """
        Analyze topic overlap between articles
        """
        try:
            # Get all topics from all articles
            all_topics = [topic for article in articles for topic in article["topics"]]
            
            # Find common topics (topics that appear in at least 30% of articles)
            topic_counts = Counter(all_topics)
            threshold = max(1, len(articles) * 0.3)  # At least 30% of articles
            
            common_topics = [
                topic for topic, count in topic_counts.items()
                if count >= threshold
            ]
            
            # Find unique topics per source
            unique_topics = {}
            for article in articles:
                source = article["source"]
                if source not in unique_topics:
                    unique_topics[source] = []
                    
                article_topics = set(article["topics"])
                
                # Find topics unique to this source
                for topic in article_topics:
                    if topic_counts[topic] == 1:  # Topic appears only once
                        unique_topics[source].append(topic)
                        
            # Make sure we have at least some data
            if not common_topics and articles:
                # Use the most frequent topic as common
                if topic_counts:
                    most_common = topic_counts.most_common(1)[0][0]
                    common_topics = [most_common]
            
            # Ensure each source has at least one topic listed
            for source in unique_topics:
                if not unique_topics[source] and articles:
                    # Add a generic topic
                    unique_topics[source] = ["company updates"]
            
            return TopicOverlap(
                common_topics=common_topics if common_topics else ["business news"],
                unique_topics=unique_topics
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing topic overlap: {str(e)}")
            return TopicOverlap(common_topics=["business"], unique_topics={})

    def _generate_impact_statement(self, sentiment1: str, sentiment2: str) -> str:
        """
        Generate an impact statement based on sentiment differences
        """
        if sentiment1 == "positive" and sentiment2 == "negative":
            return "This contrast in sentiment may indicate mixed market reactions or varying perspectives on the company's performance."
        elif sentiment1 == "negative" and sentiment2 == "positive":
            return "This contrast in sentiment may indicate mixed market reactions or varying perspectives on the company's performance."
        elif sentiment1 == "neutral" or sentiment2 == "neutral":
            return "The neutral sentiment in one article suggests a more balanced or cautious perspective compared to the other article."
        else:
            return "The different sentiment classifications may reflect varying analytical approaches or focus areas between sources." 