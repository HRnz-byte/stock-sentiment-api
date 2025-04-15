from flask import Flask, jsonify, request
from flask_cors import CORS
import praw
import os
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)
CORS(app)

# Load Reddit API credentials from environment variables
reddit = praw.Reddit(
    client_id=os.environ.get('REDDIT_CLIENT_ID'),
    client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
    user_agent='stock tracker by u/ItIsRealKiwiHours'
)

analyzer = SentimentIntensityAnalyzer()

# Regex to allow A-Z, numbers, dots (e.g. BRK.B)
VALID_TICKER_REGEX = re.compile(r'^[A-Z\.]{1,6}$')

@app.route('/api/sentiment')
def get_sentiment():
    ticker = request.args.get('ticker', '').upper().strip()

    # Validate query
    if not ticker or not VALID_TICKER_REGEX.match(ticker):
        return jsonify({'error': 'Invalid or missing ticker symbol'}), 400

    result = {
        ticker: {
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'mentions': 0
        }
    }

    try:
        posts = reddit.subreddit('stocks+investing+wallstreetbets').hot(limit=100)
        for post in posts:
            content = f"{post.title} {post.selftext}"
            if ticker in content.upper():
                score = analyzer.polarity_scores(content)['compound']
                result[ticker]['mentions'] += 1
                if score >= 0.05:
                    result[ticker]['positive'] += 1
                elif score <= -0.05:
                    result[ticker]['negative'] += 1
                else:
                    result[ticker]['neutral'] += 1

    except Exception as e:
        print(f"Error fetching Reddit data: {e}")
        return jsonify({'error': 'Failed to fetch sentiment data'}), 500

    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # For Render compatibility
    app.run(host='0.0.0.0', port=port)
