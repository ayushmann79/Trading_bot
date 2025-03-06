import tweepy
import praw
import requests
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from newsapi import NewsApiClient

# Load NLTK Sentiment Analyzer
nltk.download("vader_lexicon")
sia = SentimentIntensityAnalyzer()

# API Keys (Replace with your actual keys)
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAAPvzgEAAAAAD9Aa63z%2B36W9usIQIDQjeHBjAoc%3D7o7WsVNfJvFOTYKBjQO4laa2lZgRy7o9H64JmTnr6a9jivHjJ0"
REDDIT_CLIENT_ID = "IjURCvOsYXJaG4Ma9IqEgA"
REDDIT_CLIENT_SECRET = "8hAU52an8vyU4-9ZYBTSeDbdxA_c_A"
NEWS_API_KEY = "aa03538de0a84796bf3431865fe408fb"

# Initialize APIs
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# Initialize Twitter API v2 with Bearer Token
twitter_client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# Initialize Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent="crypto_sentiment")

from datetime import datetime, timedelta
import time

last_twitter_fetch = None
cached_twitter_score = 0

def fetch_twitter_sentiment(keyword="crypto"):
    """Fetch tweets using Twitter v2 API and analyze sentiment with hourly caching."""
    global last_twitter_fetch, cached_twitter_score
    now = datetime.now()

    # If last fetch was within 12 hours, return cached result
    if last_twitter_fetch and (now - last_twitter_fetch < timedelta(hours=12)):
        return cached_twitter_score

    query = f"{keyword} -is:retweet lang:en"
    try:
        tweets = twitter_client.search_recent_tweets(query=query, max_results=5, tweet_fields=["text"])  # Fetch only 5 posts
        time.sleep(5)  # Delay to prevent multiple requests

        if tweets.data:
            scores = [sia.polarity_scores(tweet.text)["compound"] for tweet in tweets.data]
            cached_twitter_score = sum(scores) / len(scores) if scores else 0
        last_twitter_fetch = datetime.now()
    except tweepy.TooManyRequests:
        print("Rate limit exceeded. Using last cached score.")
        return cached_twitter_score  # Use last saved score
    return cached_twitter_score



def fetch_reddit_sentiment(subreddit="cryptocurrency"):
    """Fetch Reddit posts and analyze sentiment."""
    posts = reddit.subreddit(subreddit).hot(limit=50)
    scores = [sia.polarity_scores(post.title)["compound"] for post in posts]
    return sum(scores) / len(scores) if scores else 0

def fetch_news_sentiment(keyword="crypto"):
    """Fetch news headlines and analyze sentiment."""
    articles = newsapi.get_everything(q=keyword, language="en", sort_by="relevancy")["articles"]
    scores = [sia.polarity_scores(article["title"])["compound"] for article in articles]
    return sum(scores) / len(scores) if scores else 0

def get_sentiment_score():
    """Aggregate sentiment scores from multiple sources."""
    twitter_score = fetch_twitter_sentiment()
    reddit_score = fetch_reddit_sentiment()
    news_score = fetch_news_sentiment()
    overall_sentiment = (twitter_score + reddit_score + news_score) / 3
    return overall_sentiment

if __name__ == "__main__":
    print(f"Market Sentiment Score: {get_sentiment_score():.2f}")
