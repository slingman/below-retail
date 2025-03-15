import tweepy
import json
import random
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Twitter API Credentials (Loaded Securely)
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

# ✅ Load deals from JSON file
with open("deals.json", "r") as f:
    deals = json.load(f)

# ✅ Find the best price for each product
best_deals = []
for product in deals.values():
    if len(product["prices"]) < 2:
        continue  # Skip if only one store has the product

    # ✅ Sort prices and select the cheapest option (after applying promo codes)
    sorted_prices = sorted(product["prices"], key=lambda x: x["price"])
    best_price = sorted_prices[0]  # Cheapest store
    other_prices = sorted_prices[1:3]  # Show up to two alternative prices

    # ✅ Format comparison of other store prices
    comparison_text = "\n".join([f"{p['store']} - ${p['price']}" for p in other_prices])

    best_deals.append({
        "name": product["name"],
        "best_store": best_price["store"],
        "best_price": best_price["price"],
        "best_link": best_price["link"],
        "promo": best_price.get("promo", None),  # Get promo code if available
        "comparison": comparison_text
    })

# ✅ Post tweet
if best_deals:
    deal = random.choice(best_deals)  # Pick a random best deal to tweet

    # ✅ Format tweet with promo code (if applicable)
    if deal["promo"]:
        tweet_text = f"🔥 {deal['name']} is cheapest at {deal['best_store']} for ${deal['best_price']}!\n\n🎟️ Use code **{deal['promo']}** for extra savings!\n\nOther prices:\n{deal['comparison']}\n\nBuy here: {deal['best_link']} #BestDeal #Shopping"
    else:
        tweet_text = f"🔥 {deal['name']} is cheapest at {deal['best_store']} for ${deal['best_price']}!\n\nOther prices:\n{deal['comparison']}\n\nBuy here: {deal['best_link']} #BestDeal #Shopping"

    # ✅ Post tweet
    client.create_tweet(text=tweet_text)
    print("✅ Tweet posted:", tweet_text)
else:
    print("❌ No valid deals to tweet.")
