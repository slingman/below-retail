import time
import requests
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# ✅ Updated Sneaker Sale Sources (Fixed 404s & Removed Dead Links)
SITES = [
    "https://www.nike.com/w/sale-shoes",
    "https://www.adidas.com/us/sale",
    "https://www.footlocker.com/sale/",
    "https://www.finishline.com/store/shop/sale/",
    "https://www.jdsports.com/sale/",
    "https://www.champssports.com/sale/",
    "https://www.hibbett.com/sale/",
    "https://www.dtlr.com/collections/sale",
    "https://www.shoepalace.com/collections/sale",
    "https://www.newbalance.com/sale/",
    "https://www.asics.com/us/en-us/sale/",
    "https://stockx.com/sneakers",
    "https://www.goat.com/sneakers",
    "https://www.flightclub.com/sneakers",
    "https://www.ebay.com/b/Sneakers/15709/bn_57918",
    "https://www.amazon.com/s?k=sneakers+sale"
]

# ✅ Rotating User-Agents to Avoid Blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
]

# ✅ Setup Selenium for JavaScript-heavy Sites
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in the background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")

# ✅ Automatically install & setup ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

deals = []

for site in SITES:
    print(f"🔍 Scraping {site} - Checking structure...")

    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive"
        }

        # ✅ Retry Mechanism to Fix 400 Errors
        for _ in range(3):  # Retry up to 3 times
            response = requests.get(site, headers=headers)
            if response.status_code == 200:
                break  # Exit loop if successful
            print(f"⚠️ Retrying {site} (Status Code: {response.status_code})")
            time.sleep(random.uniform(5, 15))  # Random delay to prevent blocking

        # ✅ If the site uses JavaScript, use Selenium
        if response.status_code == 403 or "javascript" in response.text.lower():
            print(f"⚠️ {site} requires JavaScript, switching to Selenium...")
            driver.get(site)
            time.sleep(5)  # Wait for JavaScript to load
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")
        else:
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

    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching {site}: {e}")
        continue

# ✅ Close Selenium WebDriver
driver.quit()

# ✅ Only save deals that have a valid image URL
valid_deals = [deal for deal in deals if deal["image"].startswith("http")]

if valid_deals:
    with open("deals.json", "w") as f:
        json.dump(valid_deals, f, indent=4)
    print(f"✅ Scraped {len(valid_deals)} sneaker deals with valid images!")
else:
    print("❌ No sneaker deals found! The website structures might have changed.")
