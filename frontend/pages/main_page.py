import streamlit as st
import requests
import json
import plotly.graph_objects as go
from typing import Dict, List
import pandas as pd
from datetime import datetime
import os

# Configure page
st.set_page_config(
    page_title="News Sentiment Analysis",
    page_icon="📰",
    layout="wide"
)

# Constants
API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

def create_sentiment_chart(sentiment_distribution: Dict) -> go.Figure:
    """Create a pie chart for sentiment distribution"""
    fig = go.Figure(data=[go.Pie(
        labels=list(sentiment_distribution.keys()),
        values=list(sentiment_distribution.values()),
        hole=.3
    )])
    fig.update_layout(title="Sentiment Distribution")
    return fig

def display_article(article: Dict):
    """Display a single article with its details"""
    with st.expander(f"📰 {article['title']}", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(article['summary'])
        with col2:
            st.write(f"**Source:** {article['source']}")
            st.write(f"**Sentiment:** {article['sentiment']}")
            st.write(f"**Topics:** {', '.join(article['topics'])}")
            if article.get('published_date'):
                st.write(f"**Published:** {article['published_date']}")
            st.markdown(f"[Read More]({article['url']})")

def display_comparative_analysis(analysis: Dict):
    """Display comparative analysis results"""
    st.header("📊 Comparative Analysis")
    
    # Sentiment Distribution Chart
    st.plotly_chart(create_sentiment_chart(analysis['sentiment_distribution']))
    
    # Coverage Differences
    st.subheader("Coverage Differences")
    for diff in analysis['coverage_differences']:
        with st.expander(f"🔍 {diff['comparison'][:100]}..."):
            st.write(diff['impact'])
    
    # Topic Overlap
    st.subheader("Topic Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Common Topics:**")
        st.write(', '.join(analysis['topic_overlap']['common_topics']))
    with col2:
        st.write("**Unique Topics by Source:**")
        for source, topics in analysis['topic_overlap']['unique_topics'].items():
            st.write(f"**{source}:** {', '.join(topics)}")

def main():
    st.title("📰 News Sentiment Analysis")
    st.write("Analyze news articles about companies and get sentiment insights with Hindi audio summary.")
    
    # Company input
    company_name = st.text_input("Enter Company Name", placeholder="e.g., Tesla, Apple, Microsoft")
    
    if st.button("Analyze"):
        if not company_name:
            st.error("Please enter a company name")
            return
            
        with st.spinner("Analyzing news articles..."):
            try:
                # Make API request
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"company_name": company_name}
                )
                response.raise_for_status()
                data = response.json()
                
                # Display results
                st.header(f"Analysis Results for {data['company']}")
                
                # Display articles
                st.header("📑 Articles")
                for article in data['articles']:
                    display_article(article)
                
                # Display comparative analysis
                display_comparative_analysis(data['comparative_analysis'])
                
                # Display final sentiment
                st.header("🎯 Final Sentiment")
                st.write(data['final_sentiment'])
                
                # Display audio player
                if data.get('audio_url'):
                    st.header("🔊 Hindi Audio Summary")
                    try:
                        audio_url = data['audio_url']
                        
                        # Use a direct proxy approach
                        st.markdown(f"""
                        <style>
                        .audio-container {{
                            margin-top: 1rem;
                            margin-bottom: 1rem;
                        }}
                        .download-btn {{
                            display: inline-block;
                            padding: 0.5rem 1rem;
                            margin-top: 0.5rem;
                            background-color: #4CAF50;
                            color: white;
                            text-decoration: none;
                            border-radius: 4px;
                        }}
                        </style>
                        <audio controls style="width:100%">
                            <source src="{audio_url}" type="audio/mpeg">
                            Your browser does not support the audio element.
                        </audio>
                        <div class="audio-container">
                            <p>If the audio doesn't play above:</p>
                            <a href="{audio_url}" download="hindi_summary.mp3" class="download-btn">Download Audio</a>
                            <a href="{audio_url}" target="_blank" class="download-btn" style="background-color: #008CBA; margin-left: 10px;">Open in New Tab</a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Error playing audio: {str(e)}")
                        st.markdown(f"[Download Audio Summary]({data['audio_url']})")
                
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the API: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 