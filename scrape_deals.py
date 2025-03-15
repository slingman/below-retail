import time
import requests
from bs4 import BeautifulSoup
import json

# ✅ Expanded Sneaker Sale Sources (Including New Balance & ASICS)
SITES = [
    "https://www.nike.com/w/sale-shoes-3yaepz5e1x6",
    "https://www.adidas.com/us/sale",
    "https://www.footlocker.com/sale/shoes",
    "https://www.finishline.com/store/shoes/sale/_/N-26d6v7r",
    "https://www.eastbay.com/sale/shoes/",
    "https://www.jdsports.com/sale/footwear/",
    "https://www.champssports.com/sale/shoes",
    "https://www.hibbett.com/sale/shoes/",
    "https://www.dtlr.com/collections/footwear-sale",
    "https://www.shoepalace.com/collections/sale",
    "https://www.newbalance.com/sale/",
    "https://www.asics.com/us/en-us/sale/c/sale/",
    "https://stockx.com/sneakers",
    "https://www.goat.com/sneakers",
    "https://www.flightclub.com/sneakers",
    "https://www.ebay.com/b/Sneakers/15709/bn_57918",
    "https://www.amazon.com/s?k=sneakers+sale",
    "https://solecollector.com/news/sneaker-release-dates",
    "https://sneakernews.com/release-dates/",
    "https://kicksdeals.com/",
    "https://www.reddit.com/r/SneakerDeals/"
]

# Make scraper look like a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

deals = []
session = requests.Session()
session.headers.update(headers)

for site in SITES:
    print(f"🔍 Scraping {site} - Checking structure...")

    try:
        response = session.get(site)
        time.sleep(5)  # Delay to prevent blocking

        if response.status_code != 200:
            print(f"❌ Failed to fetch {site} (Status Code: {response.status_code})")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Fixed Selectors for Sneaker Deal Extraction

        if "nike" in site:
            for deal in soup.find_all("div", class_="product-card__body"):
                name = deal.find("div", class_="product-card__title").text.strip()
                price = deal.find("div", class_="product-price").text.strip()
                link = "https://www.nike.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                if image.startswith("data:image"): image = ""  # Ignore base64 images
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "adidas" in site:
            for deal in soup.find_all("div", class_="gl-product-card"):
                name = deal.find("span", class_="gl-product-card__name").text.strip()
                price = deal.find("div", class_="gl-price-item").text.strip()
                link = "https://www.adidas.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                if image.startswith("data:image"): image = ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "footlocker" in site:
            for deal in soup.find_all("div", class_="fl-product-tile"):
                name = deal.find("span", class_="ProductName-primary").text.strip()
                price = deal.find("span", class_="ProductPrice").text.strip()
                link = "https://www.footlocker.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                if image.startswith("data:image"): image = ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "newbalance" in site:
            for deal in soup.find_all("div", class_="product-card"):
                name = deal.find("a", class_="product-name").text.strip()
                price = deal.find("span", class_="product-price").text.strip()
                link = "https://www.newbalance.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                if image.startswith("data:image"): image = ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "asics" in site:
            for deal in soup.find_all("div", class_="product-tile"):
                name = deal.find("a", class_="name-link").text.strip()
                price = deal.find("span", class_="sales").text.strip()
                link = "https://www.asics.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                if image.startswith("data:image"): image = ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {site}: {e}")
        continue

# ✅ Only save deals that have a valid image URL
valid_deals = [deal for deal in deals if deal["image"].startswith("http")]

if valid_deals:
    with open("deals.json", "w") as f:
        json.dump(valid_deals, f, indent=4)
    print(f"✅ Scraped {len(valid_deals)} sneaker deals with valid images!")
else:
    print("❌ No sneaker deals found! The website structures might have changed.")
