import time
import json
import random
import re
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

# ✅ Store products with multiple price options
price_comparison = {}

# ✅ Function to apply promo code discounts
def apply_promo_code(price, promo_text):
    try:
        if not promo_text:
            return price, None  # No promo available

        # Check for percentage discount
        percent_match = re.search(r"(\d+)% off", promo_text)
        if percent_match:
            discount = float(percent_match.group(1))
            return round(price * (1 - discount / 100), 2), f"{discount}% OFF"

        # Check for fixed amount discount
        amount_match = re.search(r"\$([\d.]+) off", promo_text)
        if amount_match:
            discount = float(amount_match.group(1))
            return max(price - discount, 0), f"${discount} OFF"

    except Exception as e:
        print(f"⚠️ Error applying promo code: {e}")

    return price, None  # Return original price if no valid promo

# ✅ Scraping Function (Now Uses Selenium Only)
def scrape_deals(category, urls):
    global price_comparison
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
                    name_elem = deal.find("div", class_="product-card__title")
                    name = name_elem.text.strip() if name_elem else "Unknown Product"

                    # ✅ Extract sale price
                    sale_price_elem = deal.find("div", class_="product-price is--current-price")
                    sale_price = sale_price_elem.text.strip().replace("$", "").replace(",", "") if sale_price_elem else "N/A"

                    # ✅ Extract regular price
                    regular_price_elem = deal.find("div", class_="product-price us__styling is--striked-out")
                    regular_price = regular_price_elem.text.strip().replace("$", "").replace(",", "") if regular_price_elem else sale_price

                    # Convert to float for comparison
                    try:
                        sale_price = float(sale_price) if sale_price != "N/A" else None
                        regular_price = float(regular_price) if regular_price != "N/A" else None
                    except:
                        sale_price, regular_price = None, None

                    if sale_price is None:
                        continue  # Skip if no price available

                    # ✅ Extract product link
                    link_elem = deal.find("a", class_="product-card__link-overlay")
                    link = link_elem["href"] if link_elem else "#"

                    # ✅ Extract product image
                    image_elem = deal.find("img", class_="product-card__hero-image")
                    image = image_elem["src"] if image_elem else ""

                    # ✅ Extract Promo Code (If Available)
                    promo_elem = soup.find("div", class_="promo-banner")  # Adjust class if needed
                    promo_text = promo_elem.text.strip() if promo_elem else None

                    # ✅ Apply Promo Code Discount
                    final_price, applied_promo = apply_promo_code(sale_price, promo_text)

                    # ✅ Store product for price comparison
                    if name in price_comparison:
                        price_comparison[name]["prices"].append({
                            "store": site,
                            "price": final_price,
                            "link": link,
                            "promo": applied_promo
                        })
                    else:
                        price_comparison[name] = {
                            "name": name,
                            "image": image,
                            "prices": [{
                                "store": site,
                                "price": final_price,
                                "link": link,
                                "promo": applied_promo
                            }]
                        }

                except Exception as e:
                    print(f"⚠️ Skipping product due to error: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error accessing {site}: {e}")

# ✅ Loop through each category & scrape
for category, urls in SITES.items():
    scrape_deals(category, urls)

# ✅ Save Deals to JSON
if price_comparison:
    with open("deals.json", "w") as f:
        json.dump(price_comparison, f, indent=4)
    print(f"✅ Scraped {len(price_comparison)} unique products across multiple stores!")
else:
    print("❌ No deals found! The website structures might have changed.")

# ✅ Close Selenium
driver.quit()
