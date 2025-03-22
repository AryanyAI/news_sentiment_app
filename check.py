import requests
from dotenv import load_dotenv
import os
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")

def fetch_news(company_name: str):
    url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles', [])
        return articles
    else:
        print(f"Error fetching news: {response.status_code}")
        return []

# Example usage:
company_name = "Tesla"
articles = fetch_news(company_name)
print(articles)
