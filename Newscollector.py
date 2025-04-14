import requests
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

FINNHUB_NEWS_URL = 'https://finnhub.io/api/v1/news'

PARAMS = {
    'category': 'general',  # Categories can be: general, forex, crypto, etc.
    'token': API_KEY
}

# Output CSV file path
OUTPUT_CSV = 'finnhub_financial_news.csv'

MAX_ARTICLES = 100  # Adjust as needed


def fetch_financial_news(params):
    """
    Fetch financial news articles from Finnhub API.
    
    Args:
        params (dict): Parameters for the API request.
    
    Returns:
        list: A list of news articles in JSON format.
    """
    try:
        response = requests.get(FINNHUB_NEWS_URL, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        news_articles = response.json()
        return news_articles
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Handle HTTP errors
    except Exception as err:
        print(f'Other error occurred: {err}')  # Handle other errors
    return []

def process_articles(articles, max_articles=100):
    """
    Process and extract metadata from news articles.
    
    Args:
        articles (list): List of news articles in JSON format.
        max_articles (int): Maximum number of articles to process.
    
    Returns:
        list: A list of dictionaries containing extracted metadata.
    """
    processed = []
    for article in articles[:max_articles]:
        # Extract metadata with default values if keys are missing
        title = article.get('headline', 'N/A')
        summary = article.get('summary', 'N/A')
        source = article.get('source', 'N/A')
        url = article.get('url', 'N/A')
        image_url = article.get('image', 'N/A')
        datetime_unix = article.get('datetime', None)
        related = article.get('related', 'N/A')  # Typically ticker symbols
        # Convert UNIX timestamp to readable format
        if datetime_unix:
            published_at = datetime.utcfromtimestamp(datetime_unix).strftime('%Y-%m-%d %H:%M:%S')
        else:
            published_at = 'N/A'
        
        # Append the processed article to the list
        processed.append({
            'Title': title,
            'Summary': summary,
            'Source': source,
            'URL': url,
            'Image_URL': image_url,
            'Published_At': published_at,
            'Ticker_Symbols': related
        })
    return processed

def save_to_csv(articles, file_path):
    """
    Save processed articles to a CSV file.
    
    Args:
        articles (list): List of dictionaries containing article metadata.
        file_path (str): Path to the output CSV file.
    """
    if not articles:
        print("No articles to save.")
        return
    
    # Define CSV headers based on keys of the first article
    headers = articles[0].keys()
    
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(articles)
        print(f"Successfully saved {len(articles)} articles to '{file_path}'.")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def main():
    # Fetch news articles from Finnhub
    print("Fetching financial news articles from Finnhub...")
    news_articles = fetch_financial_news(PARAMS)
    
    if not news_articles:
        print("No articles fetched. Exiting.")
        return
    
    print(f"Fetched {len(news_articles)} articles.")
    
    # Process and extract metadata
    print("Processing articles...")
    processed_articles = process_articles(news_articles, MAX_ARTICLES)
    
    # Save the processed articles to a CSV file
    print(f"Saving articles to '{OUTPUT_CSV}'...")
    save_to_csv(processed_articles, OUTPUT_CSV)

if __name__ == "__main__":
    main()
