# News Summarization and Text-to-Speech Application

A web-based application that extracts key details from multiple news articles related to a given company, performs sentiment analysis, conducts comparative analysis, and generates text-to-speech output in Hindi.

## Features

- News article extraction and summarization
- Sentiment analysis of articles
- Comparative analysis across multiple articles
- Hindi Text-to-Speech conversion
- Interactive web interface
- RESTful API endpoints

## Project Structure

```
📂 news_sentiment_app/
│── 📂 backend/
│   │── 📂 api/
│   │   │── __init__.py
│   │   │── routes.py
│   │   │── models.py
│   │── 📂 services/
│   │   │── news_scraper.py
│   │   │── text_summarizer.py
│   │   │── sentiment_analyzer.py
│   │   │── comparative_analysis.py
│   │   │── tts_service.py
│   │── 📂 utils/
│   │   │── helpers.py
│   │── config.py
│   │── main.py
│── 📂 frontend/
│   │── 📂 pages/
│   │   │── main_page.py
│   │── 📂 components/
│   │   │── visualization.py
│   │── 📂 tests/
│   │── run.py
│   │── requirements.txt
│   │── README.md
│   │── space_config.json
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd news_sentiment_app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
NEWS_API_KEY=your_api_key
```

5. Run the application:
```bash
# Option 1: Run both backend and frontend with one command
python run.py

# Option 2: Run backend and frontend separately
# Start backend
cd backend
uvicorn main:app --reload

# Start frontend (in a new terminal)
cd frontend
streamlit run pages/main_page.py
```

## API Endpoints

1. `GET /api/companies`
   - Returns list of available companies

2. `POST /api/analyze`
   - Input: JSON payload with company_name field
   - Response: Full analysis including articles, sentiment, and audio URL

3. `POST /api/tts`
   - Input: JSON payload with text field and optional language field
   - Response: Audio URL and metadata

4. `GET /api/health`
   - Method: GET
   - Response: Health status of the API

## Technologies Used

- FastAPI (Backend)
- Streamlit (Frontend)
- BeautifulSoup4 (Web Scraping)
- Hugging Face Transformers (NLP)
- gTTS (Text-to-Speech)
- Plotly (Visualization)

## Recent Fixes and Improvements

1. **News Scraping**
   - Improved URL construction for each news source
   - Added better HTTP request headers to avoid being blocked
   - Enhanced error handling and fallback mechanisms
   - Improved mock data with realistic URLs

2. **Sentiment Analysis**
   - Fixed inconsistencies between string and enum sentiment types
   - Enhanced keyword-based sentiment detection
   - Implemented more diverse sentiment outputs in mock data

3. **Text Summarization**
   - Increased default summary length for more comprehensive results
   - Added better fallback mechanisms when summarization fails
   - Improved topic extraction with frequency-based selection

4. **TTS Service**
   - Added better error handling for audio generation
   - Ensured Hindi text is properly handled
   - Created fallback audio generation when errors occur

5. **Other Improvements**
   - Fixed comparison/comparation field name mismatch
   - Added detailed logging throughout the application
   - Created a unified run script to start both backend and frontend

## Troubleshooting

If you encounter issues with the application:

1. **News Scraping Errors**: The application will fall back to mock data if scraping fails. This is normal and expected behavior for demonstration purposes.

2. **Audio Playback Issues**: If the audio doesn't play in the browser, use the download link provided on the page.

3. **Server Connection Issues**: Ensure both backend (port 8000) and frontend (typically port 8501) servers are running.

## Testing

Run tests using pytest:
```bash
pytest
```

## Deployment

The application is deployed on Hugging Face Spaces. Access it at: [Deployment URL]

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Model Details

### Text Summarization
- Model: facebook/bart-large-cnn
- Implementation: Hugging Face Transformers pipeline
- Functionality: Summarizes lengthy news articles into concise summaries

### Sentiment Analysis  
- Model: nlptown/bert-base-multilingual-uncased-sentiment
- Augmented with: Keyword-based sentiment detection
- Functionality: Classifies article sentiment as positive, negative, or neutral

### Text-to-Speech
- Library: gTTS (Google Text-to-Speech)
- Language: Hindi (hi)
- Translation: Uses deep-translator for English to Hindi conversion when needed 

## Assumptions & Limitations

1. **News Scraping**: The application attempts to fetch real-time data from RSS feeds and web scraping. If these fail, it falls back to mock data for demonstration purposes.

2. **Sentiment Analysis**: The sentiment analyzer is optimized for business and technology news but may miss nuanced sentiments in complex articles.

3. **TTS Quality**: The quality of Hindi speech depends on gTTS implementation and may have pronunciation issues with technical terms.

4. **Performance**: Processing multiple articles simultaneously may cause slower response times on resource-constrained environments.

5. **API Rate Limits**: The application doesn't implement rate limiting, which would be needed for production deployment. 