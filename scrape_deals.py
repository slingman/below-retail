import requests
from bs4 import BeautifulSoup
import json

SITES = [
    "https://kicksdeals.com/",
    "https://sneakernews.com/release-dates/",
    "https://solelinks.com/",
    "https://www.footlocker.com/sale/mens/shoes",
    "https://stockx.com/sneakers"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

deals = []

for site in SITES:
    session = requests.Session()
    session.headers.update(headers)
    response = session.get(site)

    if response.status_code != 200:
        print(f"❌ Failed to fetch {site} (Status Code: {response.status_code})")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    print(f"🔍 Scraping {site} - Checking structure...")

    # Modify based on website structure
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

# Save sneaker deals to a JSON file
if deals:
    with open("deals.json", "w") as f:
        json.dump(deals, f, indent=4)
    print(f"✅ Scraped {len(deals)} sneaker deals from multiple sites!")
else:
    print("❌ No sneaker deals found! The website structures might have changed.")
