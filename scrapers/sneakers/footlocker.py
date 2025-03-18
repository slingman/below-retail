from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

                # Visit product page to extract SKU
                driver.get(product_url)
                time.sleep(8)  # Ensure full page load

                # Extract SKU
                try:
                    sku_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Supplier-sku #:') or contains(text(), 'SKU')]"))
                    )
                    supplier_sku = sku_element.text.split(":")[-1].strip()
                    print(f"✅ Extracted Foot Locker Supplier-sku #: {supplier_sku}")

                    # Construct the correct product URL with SKU
                    correct_product_url = f"https://www.footlocker.com/product/~/{supplier_sku}.html"
                    print(f"✅ Corrected Foot Locker Product URL: {correct_product_url}")
                
                except Exception as e:
                    print(f"⚠️ SKU element not found on the page. Error: {e}")
                    supplier_sku = None

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
