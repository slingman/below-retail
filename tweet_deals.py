import tweepy
import json
import random
import os
import requests
from urllib.parse import urlparse

# ✅ Twitter API Credentials (Replace with your keys)
API_KEY = "LXNWeMaztoQ4xislo0zImh0nL"
API_SECRET = "XOpMaxXRu3Iq94rUNpXIrvaOsVooS9eS5bnoTDqna20qGFYQAT"
ACCESS_TOKEN = "14116180-ghHOQuTbcmD4d095S8vtqAd3byF0BUcVMvCl0kXZn"
ACCESS_SECRET = "EBmOjqzIdVgW5n29kzU9wx5eRXXmpywqaYNYobVW1lkqC"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAInJzwEAAAAAycsaevjYgKgwxeRGOle37jMYqTQ%3DHPiaCNrpTfv322txcJf95Ih1dHU18mfSjwa4Yyqv83L6oi063d"

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

# ✅ Load deals from JSON file
with open("deals.json", "r") as f:
    deals = json.load(f)

# ✅ Function to filter deals (only tweet if discount is 30%+)
def is_good_deal(deal):
    regular_price = deal.get("regular_price", "").replace("$", "").replace(",", "")
    sale_price = deal.get("sale_price", "").replace("$", "").replace(",", "")

    # ✅ Skip deals with missing price information
    if not regular_price or not sale_price:
        return False  

    try:
        regular_price = float(regular_price)
        sale_price = float(sale_price)
        discount = ((regular_price - sale_price) / regular_price) * 100
        return discount >= 30  # ✅ Only tweet deals that are 30%+ off
    except:
        return False

# ✅ Apply filter
filtered_deals = [deal for deal in deals if is_good_deal(deal)]

if not filtered_deals:
    print("❌ No good deals (30%+ off) to tweet.")
    exit()

# ✅ Select a random deal from the filtered ones
deal = random.choice(filtered_deals)

# ✅ Handle missing sale price safely
sale_price = deal.get("sale_price", "Unknown Price")
regular_price = deal.get("regular_price", "Unknown Price")

# ✅ Attach affiliate links based on store/category
AFFILIATE_LINKS = {
    "amazon.com": "https://affiliate-program.amazon.com/?ref=your_affiliate_id",
    "bestbuy.com": "https://www.bestbuy.com/site/misc/affiliate-program?ref=your_affiliate_id",
    "walmart.com": "https://affiliates.walmart.com/?ref=your_affiliate_id",
    "target.com": "https://affiliate.target.com/?ref=your_affiliate_id",
    "ebay.com": "https://partnernetwork.ebay.com/?ref=your_affiliate_id",
    "nike.com": "https://www.nike.com/affiliate?ref=your_affiliate_id",
    "adidas.com": "https://www.adidas.com/us/affiliates?ref=your_affiliate_id",
    "footlocker.com": "https://www.footlocker.com/affiliate?ref=your_affiliate_id",
}

# ✅ Find matching affiliate link
deal_url = deal["link"].strip()
for store in AFFILIATE_LINKS:
    if store in deal_url:
        deal_url = AFFILIATE_LINKS[store] + "&url=" + deal_url

# ✅ Format the tweet
tweet_text = f"🔥 {deal['name']} - {sale_price} (Reg: {regular_price})! Buy here: {deal_url} #Deals #Shopping"

# ✅ Check if the deal has a valid image
image_url = deal.get("image", "")  
image_path = "deal_image.jpg"

# ✅ Ignore base64 images (Twitter doesn't support them)
if image_url.startswith("data:image"):  
    print("❌ Skipping base64 image. Posting text-only tweet.")
    image_url = ""

# ✅ Download and upload image if valid
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

            # ✅ Remove the image file after posting
            os.remove(image_path)
        else:
            print("❌ Image download failed. Posting text-only tweet.")
            client.create_tweet(text=tweet_text)
    except Exception as e:
        print(f"❌ Error downloading image: {e}. Posting text-only tweet.")
        client.create_tweet(text=tweet_text)
else:
    print("❌ No valid image found. Posting text-only tweet.")
    client.create_tweet(text=tweet_text)
