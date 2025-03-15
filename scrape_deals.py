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

# ✅ Updated Deal Sources for Multiple Categories
SITES = {
    "sneakers": [
        "https://www.nike.com/w/sale-shoes",
        "https://www.adidas.com/us/sale",
        "https://www.footlocker.com/sale/",
    ],
    "tech": [
        "https://www.bestbuy.com/site/top-deals/sale",
        "https://www.amazon.com/deals",
        "https://www.walmart.com/cp/electronics-clearance/1078524",
    ],
    "gaming": [
        "https://store.steampowered.com/specials",
        "https://www.playstation.com/en-us/deals/",
        "https://www.xbox.com/en-US/promotions/sales",
    ],
    "clothing": [
        "https://www.macys.com/shop/sale/clearance",
        "https://www.nordstromrack.com/sale",
        "https://www.target.com/c/sale-clearance",
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

            # ✅ Extract Deals (Updated to Capture Sale & Regular Price)
            for deal in soup.find_all("div", class_="product-card"):
                try:
                    name = deal.find("div", class_="product-card__title").text.strip()
                    
                    # ✅ Extract sale price (discounted price)
                    sale_price_elem = deal.find("div", class_="sale-price")
                    sale_price = sale_price_elem.text.strip() if sale_price_elem else "N/A"

                    # ✅ Extract regular price (original price)
                    regular_price_elem = deal.find("div", class_="regular-price")
                    regular_price = regular_price_elem.text.strip() if regular_price_elem else sale_price  # Fallback to sale price if not found

                    # ✅ Extract product link
                    link = "https://www.nike.com" + deal.find("a")["href"]

                    # ✅ Extract product image
                    image = deal.find("img")["src"] if deal.find("img") else ""

                    deals.append({
                        "name": name,
                        "regular_price": regular_price,
                        "sale_price": sale_price,
                        "link": link,
                        "image": image,
                        "category": category
                    })
                except:
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
