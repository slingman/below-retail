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
                # Extract Product URL
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit product page to extract Supplier-sku #
                driver.get(product_url)
                time.sleep(8)  # Ensure full page load

                # **DEBUG: Print first 2000 characters of page source**
                page_source = driver.page_source
                print("\n🔍 DEBUG: First 2000 characters of Foot Locker's page source:\n")
                print(page_source[:2000])  # Print the first 2000 characters
                print("\n🔍 END DEBUG\n")

                # Extract Supplier-sku #
                match = re.search(r"Supplier-sku\s*#:\s*([\w-]+)", page_source)
                if match:
                    style_id = match.group(1).strip()
                    print(f"✅ Extracted Foot Locker Style ID (Supplier-sku #): {style_id}")
                else:
                    print("⚠️ Could not find Supplier-sku # on Foot Locker page.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
