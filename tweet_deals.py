import os
import tweepy
import json
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

# Debugging: Check if variables are being read correctly
print("API_KEY:", os.getenv("API_KEY"))  # Should print your API key, NOT 'None'

# Set up Twitter authentication
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

if None in [API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]:
    raise ValueError("❌ Twitter API credentials are missing! Check your .env file.")

# Authenticate with Twitter API
auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)

# Load deals from deals.json
with open("deals.json", "r") as f:
    deals = json.load(f)

# Iterate through deals and post tweets
for product, details in deals.items():
    if len(details["prices"]) < 2:
        print(f"⚠️ Only one store found for {product}, skipping comparison.")
        continue

    # Sort prices to find the lowest and highest
    sorted_prices = sorted(details["prices"], key=lambda x: x["price"])
    lowest = sorted_prices[0]
    highest = sorted_prices[-1]

    tweet_text = (
        f"🔥 {product} is cheapest at {lowest['store']} for ${lowest['price']}!\n\n"
        f"💰 Compared at {highest['store']} for ${highest['price']}.\n\n"
        f"🔗 Buy here: {lowest['link']}\n\n"
        f"#BestDeal #SneakerDeals"
    )

    # Attempt to download the product image
    image_url = details["image"]
    image_path = "temp_image.jpg"

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            media = client.media_upload(image_path)
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
            print(f"✅ Tweet posted: {tweet_text}")
        else:
            raise Exception("Image download failed")

    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        print("Posting text-only tweet.")
        client.create_tweet(text=tweet_text)
        print(f"✅ Text-only tweet posted: {tweet_text}")

