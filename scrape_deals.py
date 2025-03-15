import time  # Import time for delays
import requests
from bs4 import BeautifulSoup
import json

# Updated list of sneaker deal websites
SITES = [
    "https://kicksdeals.com/",
    "https://sneakernews.com/release-dates/",
    "https://solelinks.com/",
    "https://www.footlocker.com/sale/mens/shoes",
    "https://stockx.com/sneakers",
    "https://www.nike.com/w/sale-shoes-3yaepz5e1x6",  # Nike sale
    "https://www.adidas.com/us/men-sale",  # Adidas sale
    "https://www.jdsports.com/sale/mens/footwear/",
    "https://www.goat.com/sneakers",
    "https://www.ebay.com/b/Mens-Sneakers/15709/bn_57918"  # eBay sneaker deals
]

# Make scraper look like a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

deals = []
session = requests.Session()  # Keep session open to avoid detection
session.headers.update(headers)

for site in SITES:
    print(f"🔍 Scraping {site} - Checking structure...")

    try:
        response = session.get(site)
        time.sleep(5)  # 👈 Longer delay (5 sec) to prevent blocking

        if response.status_code != 200:
            print(f"❌ Failed to fetch {site} (Status Code: {response.status_code})")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Debug: Print first 1000 characters of page HTML
        print(soup.prettify()[:1000])

        # Extract sneaker deals based on website structure
        if "kicksdeals" in site:
            for deal in soup.find_all("div", class_="post-title"):
                name = deal.text.strip()
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": "Varies", "link": link, "source": site})

        elif "sneakernews" in site:
            for deal in soup.find_all("div", class_="release-card"):
                name = deal.find("h3").text.strip()
                price = deal.find("span", class_="release-price").text.strip() if deal.find("span", class_="release-price") else "TBA"
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": link, "source": site})

        elif "solelinks" in site:
            for deal in soup.find_all("div", class_="post-title"):
                name = deal.text.strip()
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": "Varies", "link": link, "source": site})

        elif "footlocker" in site:
            for deal in soup.find_all("div", class_="ProductCard"):
                name = deal.find("span", class_="ProductName-primary").text.strip()
                price = deal.find("span", class_="ProductPrice").text.strip()
                link = "https://www.footlocker.com" + deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": link, "source": site})

        elif "stockx" in site:
            for deal in soup.find_all("div", class_="tile"):
                name = deal.find("div", class_="tile-title").text.strip()
                price = deal.find("div", class_="tile-price").text.strip() if deal.find("div", class_="tile-price") else "Check Site"
                link = "https://stockx.com" + deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": link, "source": site})

        elif "nike" in site:
            for deal in soup.find_all("div", class_="product-card"):
                name = deal.find("div", class_="product-card__title").text.strip()
                price = deal.find("div", class_="product-price").text.strip()
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": "https://www.nike.com" + link, "source": site})

        elif "adidas" in site:
            for deal in soup.find_all("div", class_="product-card"):
                name = deal.find("span", class_="gl-product-card__name").text.strip()
                price = deal.find("div", class_="gl-price-item").text.strip()
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": "https://www.adidas.com" + link, "source": site})

        elif "jdsports" in site:
            for deal in soup.find_all("div", class_="productContainer"):
                name = deal.find("p", class_="product_name").text.strip()
                price = deal.find("span", class_="pri").text.strip()
                link = deal.find("a")["href"]
                deals.append({"name": name, "price": price, "link": "https://www.jdsports.com" + link, "source": site})

        elif "goat" in site:
            for deal in soup.find_all("div", class_="browse-grid-asset"):
                name = deal.find("div", class_="d3-css-1s4gn2i").text.strip(
