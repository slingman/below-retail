import os
import json
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Authenticate with Twitter
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth)

# Load scraped deals
with open("deals.json", "r") as f:
    deals = json.load(f)

# Check for multi-store deals
multi_store_deals = {}

for style_id, product in deals.items():
    prices = product.get("prices", [])

    if len(prices) > 1:
        # Sort prices in ascending order
        prices.sort(key=lambda x: x["price"])
        cheapest = prices[0]
        competitors = prices[1:]

        multi_store_deals[style_id] = {
            "name": product["name"],
            "image": product["image"],
            "cheapest": cheapest,
            "competitors": competitors,
        }

# Post tweets
if not multi_store_deals:
    print("⚠️ No deals with multiple stores found. Skipping tweets.")
else:
    for style_id, deal in multi_store_deals.items():
        product_name = deal["name"]
        image_url = deal["image"]
        cheapest_store = deal["cheapest"]["store"]
        cheapest_price = deal["cheapest"]["price"]
        cheapest_link = deal["cheapest"]["link"]

        tweet_text = f"🔥 {product_name} is cheapest at {cheapest_store} for ${cheapest_price}!\n\n"

        for competitor in deal["competitors"]:
            tweet_text += f"💰 {competitor['store']}: ${competitor['price']}\n"

        tweet_text += f"\n📢 Buy now: {cheapest_link} #BestDeal #SneakerDeals"

        # Post tweet
        try:
            api.update_status(tweet_text)
            print(f"✅ Tweet posted: {tweet_text}")
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")

    print(f"✅ Finished tweeting {len(multi_store_deals)} deals.")
