import os
import tweepy
import requests
from dotenv import load_dotenv
from scrapers.sneakers.nike import scrape_nike_air_max_1

load_dotenv()

# Twitter API auth setup
auth = tweepy.OAuth1UserHandler(
    os.getenv("TWITTER_API_KEY"),
    os.getenv("TWITTER_API_KEY_SECRET"),
    os.getenv("TWITTER_ACCESS_TOKEN"),
    os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            filename = "temp_image.jpg"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
    return None

def construct_tweet(deal):
    lines = [
        f"{deal['title']} ({deal['style']})",
        f"Price: {deal['price']}",
    ]
    if deal.get("original_price"):
        lines.append(f"Was: {deal['original_price']}")
    if deal.get("discount"):
        lines.append(f"Discount: {deal['discount']}")
    lines.append(deal["url"])
    return "\n".join(lines)

def tweet_deals():
    print("🔍 Scraping deals for tweets...")
    deals = scrape_nike_air_max_1()

    for deal in deals:
        tweet = construct_tweet(deal)
        print(f"\n📝 Tweeting:\n{tweet}\n")

        image_path = None
        if "image" in deal:
            image_path = download_image(deal["image"])

        try:
            if image_path:
                media = api.media_upload(image_path)
                api.update_status(status=tweet, media_ids=[media.media_id])
                os.remove(image_path)
            else:
                api.update_status(status=tweet)
        except Exception as e:
            print(f"❌ Error tweeting: {e}")

if __name__ == "__main__":
    tweet_deals()
