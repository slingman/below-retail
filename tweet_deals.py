import tweepy
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twitter API Credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Twitter Authentication
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# Load deals
with open("deals.json", "r") as file:
    deals = json.load(file)

# Compare deals and tweet the best price
for style_id, product in deals.items():
    prices = product.get("prices", [])
    if not prices:
        print(f"⚠️ Warning: No prices found for {product.get('name', 'Unknown Product')}, skipping.")
        continue
 
    if len(prices) < 2:
        print(f"⚠️ Only one store found for {product['name']} ({style_id}), skipping comparison.")
        continue

    # Find the cheapest price
    cheapest = min(prices, key=lambda x: x["price"])
    
    # Create tweet
    tweet_text = (
        f"🔥 {product['name']} ({style_id}) is cheapest at {cheapest['store']} for ${cheapest['price']}!\n\n"
        f"Compared at:\n"
        + "\n".join([f"{p['store']}: ${p['price']}" for p in prices])
        + f"\n\nBuy now: {cheapest['link']} #BestDeal #NikeAirMax1"
    )

    try:
        api.update_status(tweet_text)
        print(f"✅ Tweet posted: {tweet_text}\n")
    except tweepy.TweepyException as e:
        print(f"❌ Error posting tweet: {e}")

print("✅ Finished tweeting deals.")
