import time
import requests
from bs4 import BeautifulSoup
import json

# List of sneaker deal websites
SITES = [
    "https://kicksdeals.com/",
    "https://sneakernews.com/release-dates/",
    "https://solelinks.com/",
    "https://www.footlocker.com/sale/mens/shoes",
    "https://stockx.com/sneakers",
    "https://www.nike.com/w/sale-shoes-3yaepz5e1x6",
    "https://www.adidas.com/us/men-sale",
    "https://www.jdsports.com/sale/mens/footwear/",
    "https://www.goat.com/sneakers",
    "https://www.ebay.com/b/Mens-Sneakers/15709/bn_57918"
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

        # Extract sneaker deals including images
        if "kicksdeals" in site:
            for deal in soup.find_all("div", class_="post-title"):
                name = deal.text.strip()
                link = deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                deals.append({"name": name, "price": "Varies", "link": link, "image": image, "source": site})

        elif "sneakernews" in site:
            for deal in soup.find_all("div", class_="release-card"):
                name = deal.find("h3").text.strip()
                price = deal.find("span", class_="release-price").text.strip() if deal.find("span", class_="release-price") else "TBA"
                link = deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "solelinks" in site:
            for deal in soup.find_all("div", class_="post-title"):
                name = deal.text.strip()
                link = deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                deals.append({"name": name, "price": "Varies", "link": link, "image": image, "source": site})

        elif "footlocker" in site:
            for deal in soup.find_all("div", class_="ProductCard"):
                name = deal.find("span", class_="ProductName-primary").text.strip()
                price = deal.find("span", class_="ProductPrice").text.strip()
                link = "https://www.footlocker.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""
                deals.append({"name": name, "price": price, "link": link, "image": image, "source": site})

        elif "sto
