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

        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product URL from the search results
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Ensure full page load

                page_source = driver.page_source

                # Extract Foot Locker Product # (this is what they use in the URL)
                product_match = re.search(r'"productId"\s*:\s*"([^"]+)"', page_source)
                product_number = product_match.group(1) if product_match else None

                # Extract Supplier SKU # (Foot Locker’s own SKU, not the Product #)
                sku_match = re.search(r'"sku"\s*:\s*"([^"]+)"', page_source)
                supplier_sku = sku_match.group(1).strip() if sku_match else None

                # Construct Correct Foot Locker URL
                if product_number:
                    correct_product_url = f"https://www.footlocker.com/product/~/ {product_number}.html".replace("~/ ", "").strip()
                    print(f"✅ Corrected Foot Locker Product URL: {correct_product_url}")
                else:
                    print("⚠️ Could not extract Foot Locker Product # for URL.")

                if supplier_sku:
                    print(f"✅ Extracted Foot Locker Supplier SKU #: {supplier_sku}")
                else:
                    print("⚠️ Could not extract Supplier SKU #.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
