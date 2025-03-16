import tweepy
import json
import random
import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse

# ✅ Load API Credentials from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Authenticate with Twitter API
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
    bearer_token=BEARER_TOKEN  # Needed for uploading images
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Load deals from deals.json
with open("deals.json", "r") as f:
    deals = json.load(f)

# ✅ Pick a random deal to tweet
if deals:
    deal = random.choice(list(deals.values()))

    # ✅ Identify the cheapest price among stores
    best_store = min(deal["prices"], key=lambda x: float(x["price"]))
    best_price = best_store["price"]
    best_store_name = best_store["store"]
    best_link = best_store["link"]
    promo_code = best_store.get("promo", None)

    # ✅ Determine regular price and calculate discount (if available)
    try:
        regular_price = float(deal.get("regular_price", best_price))
        discount = ((regular_price - best_price) / regular_price) * 100 if regular_price > best_price else 0
    except ValueError:
        discount = 0  # If there's no valid regular price, assume no discount

    # ✅ Format tweet
    tweet_text = f"🔥 {deal['name']} is cheapest at {best_store_name} for ${best_price:.2f}!\n\n"

    # List other store prices
    other_prices = [
        f"{price_info['store']} - ${price_info['price']:.2f}"
        for price_info in deal["prices"] if price_info["store"] != best_store_name
    ]
    if other_prices:
        tweet_text += "Other prices:\n" + "\n".join(other_prices) + "\n\n"

    # Include discount percentage if applicable
    if discount > 0:
        tweet_text += f"💰 {discount:.0f}% OFF!\n\n"

    # Include promo code if available
    if promo_code:
        tweet_text += f"💳 Use promo code: {promo_code}\n\n"

    # Add final link
    tweet_text += f"🔗 Buy here: {best_link} #BestDeal #Shopping"

    # ✅ Download the product image (if available)
    image_url = deal.get("image", "")
    image_path = "product.jpg"

    # Ignore base64 images (Twitter only accepts regular image URLs)
    if image_url.startswith("data:image"):
        print("❌ Skipping base64 image. Posting text-only tweet.")
        image_url = ""

    if image_url:
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)

                # ✅ Upload image to Twitter
                media = api.media_upload(image_path)

                # ✅ Post tweet with image
                client.create_tweet(text=tweet_text, media_ids=[media.media_id])
                print("✅ Tweet with image posted:", tweet_text)
            else:
                print("❌ Image download failed. Posting text-only tweet.")
                client.create_tweet(text=tweet_text)
        except Exception as e:
            print(f"❌ Error downloading image: {e}. Posting text-only tweet.")
            client.create_tweet(text=tweet_text)
    else:
        print("❌ No valid image found. Posting text-only tweet.")
        client.create_tweet(text=tweet_text)
else:
    print("❌ No deals found to tweet.")
