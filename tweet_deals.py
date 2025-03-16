import tweepy
import json
import random
import os
import requests
import time  # ✅ Import time for delays
from dotenv import load_dotenv
from urllib.parse import urlparse

# ✅ Load API Credentials from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# ✅ Authenticate with Twitter API
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    bearer_token=BEARER_TOKEN
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# ✅ Load deals from deals.json
with open("deals.json", "r") as f:
    deals = json.load(f)

# ✅ Tweet Multiple Deals Per Run (Limited to 3)
if deals:
    num_tweets = min(1, len(deals))  # Tweets 1 deal per run (safer)
    random_deals = random.sample(list(deals.values()), num_tweets)

    for deal in random_deals:
        best_store = min(deal["prices"], key=lambda x: float(x["price"]))
        best_price = best_store["price"]
        best_store_name = best_store["store"]
        best_link = best_store["link"]
        promo_code = best_store.get("promo", None)

        # Find the highest price from other stores for comparison
        other_stores = [
            (price_info["store"], float(price_info["price"]))
            for price_info in deal["prices"] if price_info["store"] != best_store_name
        ]
        highest_store, highest_price = max(other_stores, key=lambda x: x[1], default=(None, None))

        # Determine discount percentage
        try:
            regular_price = float(deal.get("regular_price", best_price))
            discount = ((regular_price - best_price) / regular_price) * 100 if regular_price > best_price else 0
        except ValueError:
            discount = 0  

        # ✅ Format tweet
        tweet_text = f"🔥 {deal['name']} is cheapest at {best_store_name} for ${best_price:.2f}!\n\n"

        if highest_store:
            tweet_text += f"⚡ Compared at {highest_store} for ${highest_price:.2f}!\n\n"

        if discount > 0:
            tweet_text += f"💰 {discount:.0f}% OFF!\n\n"

        if promo_code:
            tweet_text += f"💳 Use promo code: {promo_code}\n\n"

        tweet_text += f"🔗 Buy here: {best_link} #BestDeal #Shopping"

        # ✅ Download and attach the product image
        image_url = deal.get("image", "")
        image_path = "product.jpg"

        if image_url.startswith("data:image"):
            print("❌ Skipping base64 image. Posting text-only tweet.")
            image_url = ""

        try:
            media_id = None
            if image_url:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(image_path, "wb") as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)

                    media = api.media_upload(image_path)
                    media_id = media.media_id

            if media_id:
                client.create_tweet(text=tweet_text, media_ids=[media_id])
            else:
                client.create_tweet(text=tweet_text)

            print("✅ Tweet posted:", tweet_text)

            # ✅ Add a delay after each tweet to avoid rate limits
            time.sleep(random.uniform(120, 300))  # 🔹 Now waits 2-5 minutes before next tweet

        except tweepy.errors.TooManyRequests as e:
            print("🚨 Twitter rate limit reached! Waiting for 1 hour before retrying...")
            time.sleep(3600)  # 🔹 Now waits 1 hour if rate limit is hit
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")

else:
    print("❌ No deals found to tweet.")
