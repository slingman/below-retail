import tweepy
import json
import random

# ✅ Replace these with your new Twitter API credentials
API_KEY = "LXNWeMaztoQ4xislo0zImh0nL"
API_SECRET = "XOpMaxXRu3Iq94rUNpXIrvaOsVooS9eS5bnoTDqna20qGFYQAT"
ACCESS_TOKEN = "14116180-ghHOQuTbcmD4d095S8vtqAd3byF0BUcVMvCl0kXZn"
ACCESS_SECRET = "EBmOjqzIdVgW5n29kzU9wx5eRXXmpywqaYNYobVW1lkqC"

# Authenticate with Twitter API
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Load sneaker deals from deals.json
with open("deals.json", "r") as f:
    deals = json.load(f)

# Pick a random deal to tweet
if deals:
    deal = random.choice(deals)
    tweet_text = f"🔥 {deal['name']} - {deal['price']}! Grab it here: {deal['link']} #SneakerDeals"

    # Post the tweet
    client.create_tweet(text=tweet_text)
    print("✅ Tweet posted:", tweet_text)
else:
    print("❌ No sneaker deals found in deals.json")
