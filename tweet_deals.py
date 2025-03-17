import tweepy
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Authenticate Twitter API
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
client = tweepy.API(auth)

# Load deals data
with open("deals.json", "r") as f:
    deals = json.load(f)

# Post tweets
for style_id, product in deals.items():
    prices = product["prices"]
    if len(prices) < 2:
        print(f"⚠️ Only one store found for {product['name']} ({style_id}), skipping comparison.")
        continue

    # Sort prices and get the lowest and highest
    sorted_prices = sorted(prices, key=lambda x: x["price"])
    lowest_price_store = sorted_prices[0]
    highest_price_store = sorted_prices[-1]

    tweet_text = (
        f"🔥 {product['name']} ({style_id}) is cheapest at {lowest_price_store['store']} for ${lowest_price_store['price']}!\n\n"
        f"Compared at {highest_price_store['store']}: ${highest_price_store['price']}\n\n"
        f"Buy now: {lowest_price_store['link']} #BestDeal #Shopping"
    )

    try:
        client.update_status(tweet_text)
        print(f"✅ Tweet posted: {tweet_text}")
    except tweepy.TweepError as e:
        print(f"❌ Error posting tweet: {e}")
