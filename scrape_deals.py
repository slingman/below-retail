import time
import json
import random
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

# ✅ Setup Selenium for JavaScript-rendered Sites
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

deals = []

# ✅ Scraping Function (Always Uses Selenium)
def scrape_deals(category, urls):
    global deals
    print(f"🔍 Scraping {category.upper()} Deals with Selenium...")

    for site in urls:
        print(f"🔍 Accessing {site} with Selenium...")

        try:
            driver.get(site)
            time.sleep(random.uniform(5, 10))  # Let JavaScript load

            # Scroll to load more items (simulating user behavior)
            for _ in range(3):
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(random.uniform(2, 4))

            # Get page source after JavaScript execution
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")

            # ✅ Extract Deals
            for deal in soup.find_all("div", class_="product-card"):
                try:
                    print("\n🔍 Full Product Card HTML:\n", deal.prettify())  # Debugging step

                    name_elem = deal.find("div", class_="product-card__title")
                    name = name_elem.text.strip() if name_elem else "Unknown Product"

                    # ✅ Extract sale price
                    sale_price_elem = deal.find("div", class_="product-price is--current-price")
                    sale_price = sale_price_elem.text.strip() if sale_price_elem else "N/A"

                    # ✅ Extract regular price
                    regular_price_elem = deal.find("div", class_="product-price us__styling is--striked-out")
                    regular_price = regular_price_elem.text.strip() if regular_price_elem else sale_price

                    print(f"✅ Final Prices - Regular: {regular_price}, Sale: {sale_price}")

                    # ✅ Extract product link
                    link_elem = deal.find("a", class_="product-card__link-overlay")
                    link = link_elem["href"] if link_elem else "#"

                    # ✅ Extract product image
                    image_elem = deal.find("img", class_="product-card__hero-image")
                    image = image_elem["src"] if image_elem else ""

                    deals.append({
                        "name": name,
                        "regular_price": regular_price,
                        "sale_price": sale_price,
                        "link": link,
                        "image": image,
                        "category": category
                    })
                except Exception as e:
                    print(f"⚠️ Skipping product due to error: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error accessing {site}: {e}")

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
