from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for efficiency
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(search_url)
        time.sleep(5)  # Allow time for page to load

        deals = []
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product Name
                try:
                    product_name = card.find_element(By.CLASS_NAME, "ProductCard-title").text
                except:
                    product_name = "Unknown Product"

                # Extract Product URL
                try:
                    raw_product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                except:
                    raw_product_url = None

                if not raw_product_url:
                    continue  # Skip if no URL is found

                # Extract Foot Locker Product ID from URL
                match = re.search(r"/([^/]+)\.html", raw_product_url)
                if match:
                    footlocker_product_id = match.group(1)
                else:
                    continue  # Skip if product ID is not found

                # Construct proper Foot Locker product page URL
                product_url = f"https://www.footlocker.com/product/~/ {footlocker_product_id}.html".replace(" ~/ ", "~/")  # Fix any spaces

                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit the product page to extract the Supplier-sku # (Nike Style ID)
                driver.get(product_url)
                time.sleep(8)  # Allow the product page to fully load

                # Extract Supplier-sku # (Nike Style ID) from page source
                style_id = None
                page_source = driver.page_source

                match = re.search(r"Supplier-sku\s*#:\s*([\w-]+)", page_source)
                if match:
                    style_id = match.group(1).strip()
                    print(f"✅ Extracted Foot Locker Style ID (Supplier-sku #): {style_id}")
                else:
                    print("⚠️ Could not find Supplier-sku # on Foot Locker page.")

                # Extract Image URL
                try:
                    image_url = driver.find_element(By.CLASS_NAME, "ProductImage").get_attribute("src")
                except:
                    image_url = None

                # Extract Price
                try:
                    sale_price = driver.find_element(By.CLASS_NAME, "ProductPrice-sale").text
                    sale_price = float(sale_price.replace("$", "").replace(",", ""))
                except:
                    sale_price = None

                try:
                    original_price = driver.find_element(By.CLASS_NAME, "ProductPrice-regular").text
                    original_price = float(original_price.replace("$", "").replace(",", ""))
                except:
                    original_price = sale_price  # If no original price, assume no discount

                # Skip products with missing Style ID
                if not style_id:
                    continue

                # Store deal information
                deals.append({
                    "store": "Foot Locker",
                    "product_name": product_name,
                    "product_url": product_url,
                    "image_url": image_url,
                    "sale_price": sale_price,
                    "original_price": original_price,
                    "style_id": style_id,  # Supplier-sku # is Nike's Style ID
                })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

        return deals

    finally:
        driver.quit()
