import os
import tweepy
import json
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Twitter API credentials
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if None in [API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]:
    raise ValueError("❌ ERROR: Twitter API credentials are missing! Check your .env file.")

# **Set up API v1.1 for media upload**
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# **Set up API v2 for text tweets**
client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
                       access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# Load scraped deals
DEALS_FILE = "deals.json"
if not os.path.exists(DEALS_FILE):
    raise FileNotFoundError(f"❌ ERROR: {DEALS_FILE} not found! Run `scrape_deals.py` first.")

with open(DEALS_FILE, "r") as f:
    deals = json.load(f)

# Tweet deals
TWEETED = 0
for product, data in deals.items():
    prices = data.get("prices", [])

    if len(prices) < 2:
        print(f"⚠️ Only one store found for {product}, skipping comparison.")
        continue  # Skip if no price comparison

    # Sort prices (lowest first)
    prices.sort(key=lambda x: x["price"])
    best_deal = prices[0]
    other_prices = prices[1:]

    # Construct tweet text
    tweet_text = f"🔥 {product} is cheapest at {best_deal['store']} for ${best_deal['price']}!\n\n"

    for p in other_prices[:2]:  # Show at most two other stores
        tweet_text += f"Compared at {p['store']}: ${p['price']}\n"

    tweet_text += f"\nBuy now: {best_deal['link']} #BestDeal #Shopping"

    # Download product image
    image_url = data.get("image")
    image_path = "product_image.jpg"

    try:
        if image_url:
            img_data = requests.get(image_url).content
            with open(image_path, "wb") as img_file:
                img_file.write(img_data)

            # Upload image using Twitter API v1.1
            media = api.media_upload(image_path)
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        else:
            client.create_tweet(text=tweet_text)

        TWEETED += 1
        print(f"✅ Tweet posted: {tweet_text}")

    except Exception as e:
        print(f"❌ Error posting tweet: {e}")

    # Avoid rate limits
    if TWEETED >= 10:
        print("🚨 Twitter rate limit reached! Stopping tweets.")
        break

print(f"✅ Finished tweeting {TWEETED} deals.")
