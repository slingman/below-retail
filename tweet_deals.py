import tweepy
import json
import os
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate Twitter API
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    bearer_token=BEARER_TOKEN
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Load deals
with open("deals.json", "r") as f:
    sneaker_deals = json.load(f)

# Tweet best deals
for sneaker, data in sneaker_deals.items():
    prices = sorted(data["prices"], key=lambda x: x["price"])
    
    if len(prices) < 2:
        print(f"⚠️ Only one store found for {sneaker}, skipping comparison.")
        continue

    best_deal = prices[0]
    other_prices = "\n".join([f"- {p['store']}: ${p['price']}" for p in prices[1:3]])

    tweet_text = f"""
    🔥 {data['name']} (Style ID: {data['style_id']}) is cheapest at {best_deal['store']} for ${best_deal['price']}!
    
    Compared at:
    {other_prices}
    
    Buy here: {best_deal['link']} #BestDeal #SneakerDeals
    """.strip()

    # Download product image
    image_url = data["image"]
    image_path = "sneaker.jpg"

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            media = api.media_upload(image_path)
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print(f"✅ Tweeted: {tweet_text}")
        else:
            client.create_tweet(text=tweet_text)
            print(f"✅ Tweeted (No image): {tweet_text}")

    except Exception as e:
        print(f"❌ Error posting tweet: {e}")

    # Respect Twitter rate limits
    time.sleep(10)
