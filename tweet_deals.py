import os
import tweepy
import json
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Assign API credentials from environment variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Ensure API keys are loaded correctly
if not TWITTER_API_KEY or not TWITTER_API_KEY_SECRET or not TWITTER_ACCESS_TOKEN or not TWITTER_ACCESS_TOKEN_SECRET:
    raise ValueError("❌ ERROR: Missing Twitter API credentials! Check your .env file.")

# Debugging: Print confirmation
print("✅ Loaded Twitter API credentials.")

# Tweepy authentication
try:
    auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_KEY_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )
    print("✅ Twitter authentication successful!")
except Exception as e:
    raise ValueError(f"❌ Twitter authentication failed: {e}")

# Load deals from deals.json
DEALS_FILE = "deals.json"

if not os.path.exists(DEALS_FILE):
    raise FileNotFoundError(f"❌ ERROR: {DEALS_FILE} not found. Run scrape_deals.py first!")

with open(DEALS_FILE, "r") as file:
    deals = json.load(file)

# Filter deals with multiple store listings for comparison
comparable_deals = []
for product, data in deals.items():
    if "prices" in data and len(data["prices"]) > 1:
        comparable_deals.append(data)

# Check if there are any comparable deals
if not comparable_deals:
    print("⚠️ No deals with multiple stores found. Skipping tweets.")
    exit()

# Tweet each deal
tweet_count = 0

for deal in comparable_deals:
    name = deal["name"]
    style_id = deal.get("style_id", "N/A")
    image_url = deal["image"]
    prices = sorted(deal["prices"], key=lambda x: x["price"])  # Sort by lowest price
    cheapest = prices[0]
    
    tweet_text = (
        f"🔥 {name} ({style_id}) is cheapest at {cheapest['store']} for ${cheapest['price']}!\n\n"
        f"Compared at:\n"
    )
    
    for p in prices:
        tweet_text += f"{p['store']}: ${p['price']}\n"
    
    tweet_text += f"\nBuy now: {cheapest['link']} #BestDeal #Shopping"

    try:
        # Upload image if available
        media = None
        if image_url:
            image_path = "temp_image.jpg"
            os.system(f"curl -s {image_url} -o {image_path}")  # Download image
            media = api.media_upload(image_path)
            os.remove(image_path)

        # Post the tweet
        if media:
            client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        else:
            client.create_tweet(text=tweet_text)

        print(f"✅ Tweet posted: {tweet_text}")
        tweet_count += 1

    except tweepy.TweepyException as e:
        print(f"❌ Error posting tweet: {e}")

print(f"✅ Finished tweeting {tweet_count} deals.")
