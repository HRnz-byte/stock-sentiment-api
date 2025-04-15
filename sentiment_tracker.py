from flask import Flask, jsonify
from flask_cors import CORS
import praw
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)

# Reddit API credentials pulled from environment variables
reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    user_agent='stock tracker by u/ItIsRealKiwiHours'
)

# Stocks to track
TICKERS = ['SPY', 'VOO', 'BRK.B']
analyzer = SentimentIntensityAnalyzer()

def fetch_reddit_data():
    data = {ticker: {'positive': 0, 'negative': 0, 'neutral': 0, 'mentions': 0} for ticker in TICKERS}
    
    try:
        posts = reddit.subreddit('stocks+investing+wallstreetbets').hot(limit=100)
        for post in posts:
            content = f"{post.title} {post.selftext}"
            for ticker in TICKERS:
                if ticker.upper() in content.upper():
                    score = analyzer.polarity_scores(content)['compound']
                    data[ticker]['mentions'] += 1
                    if score >= 0.05:
                        data[ticker]['positive'] += 1
                    elif score <= -0.05:
                        data[ticker]['negative'] += 1
                    else:
                        data[ticker]['neutral'] += 1
    except Exception as e:
        print("Error fetching Reddit data:", e)
    
    return data

@app.route('/api/sentiment')
def sentiment():
    return jsonify(fetch_reddit_data())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # For Render compatibility
    app.run(host='0.0.0.0', port=port)