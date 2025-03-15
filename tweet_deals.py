import tweepy
import json
import random
import os
import requests
from urllib.parse import urlparse

# ✅ Replace these with your new Twitter API credentials
API_KEY = "LXNWeMaztoQ4xislo0zImh0nL"
API_SECRET = "XOpMaxXRu3Iq94rUNpXIrvaOsVooS9eS5bnoTDqna20qGFYQAT"
ACCESS_TOKEN = "14116180-ghHOQuTbcmD4d095S8vtqAd3byF0BUcVMvCl0kXZn"
ACCESS_SECRET = "EBmOjqzIdVgW5n29kzU9wx5eRXXmpywqaYNYobVW1lkqC"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAInJzwEAAAAAycsaevjYgKgwxeRGOle37jMYqTQ%3DHPiaCNrpTfv322txcJf95Ih1dHU18mfSjwa4Yyqv83L6oi063d"

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

# Load sneaker deals from deals.json
with open("deals.json", "r") as f:
    deals = json.load(f)

# Pick a random deal to tweet
if deals:
    deal = random.choice(deals)

    # ✅ Fix URL formatting dynamically
    link = deal["link"].strip()
    if not link.startswith("http"):
        parsed_source = urlparse(deal["source"]).netloc
        link = f"https://{parsed_source}{link}"

    tweet_text = f"🔥 {deal['name']} - {deal['price']}! Grab it here: {link} #SneakerDeals"

    # ✅ Download the product image (if available and valid)
    image_url = deal.get("image", "")  # Ensure the deal JSON contains an "image" field
    image_path = "sneaker.jpg"

    # Ignore base64 images (Twitter only accepts regular image URLs)
    if image_url.startswith("data:image"):  
        print("❌ Skipping base64 image. Posting text-only tweet.")
        image_url = ""  # Ignore base64 images

    if image_url:
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(image_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)

                # ✅ Upload the image to Twitter
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
    print("❌ No sneaker deals found in deals.json")
