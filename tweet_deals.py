# tweet_deals.py

import os
import requests
import tweepy
from scrapers.sneakers.nike import scrape_nike_air_max_1

# Twitter API credentials from your dev account
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
api = tweepy.API(auth)

def download_image(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = "temp.jpg"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
    return None

def post_deal_to_twitter(deal):
    tweet_text = f"{deal['title']} ({deal['style']})\n"
    tweet_text += f"💰 {deal['price']} (was {deal['original_price']})"
    if deal['discount']:
        tweet_text += f" — {deal['discount']} off"
    tweet_text += f"\n🔗 {deal['url']}"

    media_id = None
    if deal.get("image"):
        img_path = download_image(deal["image"])
        if img_path:
            media = api.media_upload(img_path)
            media_id = media.media_id
            os.remove(img_path)

    try:
        if media_id:
            api.update_status(status=tweet_text, media_ids=[media_id])
        else:
            api.update_status(status=tweet_text)
        print(f"✅ Tweeted: {deal['title']}")
    except Exception as e:
        print(f"❌ Error tweeting {deal['title']}: {e}")

def main():
    print("🧵 Scraping Nike Air Max 1 deals...")
    deals = scrape_nike_air_max_1()

    print("🐦 Tweeting deals...")
    for deal in deals:
        post_deal_to_twitter(deal)

if __name__ == "__main__":
    main()
