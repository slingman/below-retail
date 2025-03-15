import time
import requests
import random
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ✅ Verified Deal Sources for Multiple Categories
SITES = {
    "sneakers": [
        "https://www.nike.com/w/sale-3yaep",  # Nike Sale
        "https://www.adidas.com/us/sale",  # Adidas Sale
        "https://www.footlocker.com/sale",  # Foot Locker Sale
    ],
    "tech": [
        "https://www.bestbuy.com/site/top-deals",  # Best Buy Top Deals
        "https://www.amazon.com/deals",  # Amazon Today's Deals
        "https://www.walmart.com/cp/electronics-clearance/1078524",  # Walmart Electronics Clearance
    ],
    "gaming": [
        "https://store.steampowered.com/specials",  # Steam Specials
        "https://www.playstation.com/en-us/deals/",  # PlayStation Deals
        "https://www.xbox.com/en-US/promotions/sales",  # Xbox Sales & Specials
    ],
    "clothing": [
        "https://www.macys.com/shop/sale/clearance",  # Macy's Clearance
        "https://www.nordstromrack.com/sale",  # Nordstrom Rack Sale
        "https://www.target.com/c/sale/-/N-4xw74",  # Target Sale
    ]
}

# ✅ Setup Selenium for JavaScript-heavy Sites
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

deals = []

# ✅ Scraping Function
def scrape_deals(category, urls):
    global deals
    print(f"🔍 Scraping {category.upper()} Deals...")
    
    for site in urls:
        print(f"🔍 Checking {site}")

        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
            ]),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com",
            "Connection": "keep-alive"
        }

        try:
            response = requests.get(site, headers=headers, timeout=10)
            
            # If the site blocks normal requests, use Selenium
            if response.status_code == 403 or "javascript" in response.text.lower():
                print(f"⚠️ {site} requires JavaScript, switching to Selenium...")
                driver.get(site)
                time.sleep(random.uniform(5, 10))  # Let JavaScript load

                # Scroll to load more items
                for _ in range(3):
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                    time.sleep(random.uniform(2, 4))

                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
            else:
                soup = BeautifulSoup(response.text, "html.parser")

            # ✅ Extract Promo Codes
            promo_code = "N/A"
            for promo_class in ["promo-banner", "coupon-code", "promo-text"]:
                promo_elem = soup.find("div", class_=promo_class)
                if promo_elem:
                    promo_code = promo_elem.text.strip().upper()
                    break  

            # ✅ Extract Deals (Including Sale & Regular Price)
            for deal in soup.find_all("div", class_="product-card"):
                try:
                    name = deal.find("div", class_="product-card__title").text.strip()
                    
                    # ✅ Extract sale price from multiple possible elements
                    sale_price = "N/A"
                    for sale_class in ["sale-price", "discount-price", "current-price", "price-sale"]:
                        sale_price_elem = deal.find("div", class_=sale_class)
                        if sale_price_elem:
                            sale_price = sale_price_elem.text.strip()
                            print(f"🔍 Found Sale Price: {sale_price}")  # Debugging output
                            break  

                    # ✅ Extract regular price from multiple possible elements
                    regular_price = "N/A"
                    for reg_class in ["regular-price", "original-price", "was-price", "price-original"]:
                        regular_price_elem = deal.find("div", class_=reg_class)
                        if regular_price_elem:
                            regular_price = regular_price_elem.text.strip()
                            print(f"🔍 Found Regular Price: {regular_price}")  # Debugging output
                            break  

                    # ✅ If only one price is found, assume it's the sale price
                    if regular_price == "N/A" and sale_price != "N/A":
                        regular_price = sale_price
                    elif sale_price == "N/A" and regular_price != "N/A":
                        sale_price = regular_price  

                    print(f"✅ Final Prices - Regular: {regular_price}, Sale: {sale_price}")

                    # ✅ Extract product link
                    link = "https://www.nike.com" + deal.find("a")["href"]

                    # ✅ Extract product image
                    image = deal.find("img")["src"] if deal.find("img") else ""

                    deals.append({
                        "name": name,
                        "regular_price": regular_price,
                        "sale_price": sale_price,
                        "promo_code": promo_code if promo_code != "N/A" else None,  # Include only if valid
                        "link": link,
                        "image": image,
                        "category": category
                    })
                except Exception as e:
                    print(f"⚠️ Skipping product due to error: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching {site}: {e}")

# ✅ Loop through each category & scrape
for category, urls in SITES.items():
    scrape_deals(category, urls)

# ✅ Save Deals to JSON
if deals:
    with open("deals.json", "w") as f:
        json.dump(deals, f, indent=4)
    print(f"✅ Scraped {len(deals)} deals across all categories!")
else:
    print("❌ No deals found! The website structures might have changed.")

# ✅ Close Selenium
driver.quit()
