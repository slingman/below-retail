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
        time.sleep(5)  # Allow page to load

        # Get first product card
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")
        if not product_cards:
            print("⚠️ No products found on Foot Locker search page.")
            return None
        
        first_product = product_cards[0]

        # Extract Product URL
        product_link_element = first_product.find_element(By.CLASS_NAME, "ProductCard-link")
        raw_product_url = product_link_element.get_attribute("href")

        # Extract SKU from the product URL (if possible)
        match = re.search(r"/product/.*?/([\w-]+)\.html", raw_product_url)
        if match:
            sku = match.group(1)
            correct_product_url = f"https://www.footlocker.com/product/~/ {sku}.html"
            print(f"✅ Extracted Foot Locker Product URL: {correct_product_url}")
        else:
            correct_product_url = raw_product_url
            print(f"⚠️ Could not determine correct product URL format, using original: {raw_product_url}")

        # Visit product page
        driver.get(correct_product_url)

        # Wait for SKU element
        try:
            sku_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Supplier-sku #:') or contains(text(), 'SKU #:')]"))
            )
            supplier_sku = sku_element.text.split(":")[-1].strip()
            print(f"✅ Extracted Foot Locker Supplier-sku #: {supplier_sku}")
        except:
            print("⚠️ SKU element not found on the page.")
            supplier_sku = None

        # Return extracted product details
        return {
            "store": "Foot Locker",
            "product_url": correct_product_url,
            "supplier_sku": supplier_sku
        }

    except Exception as e:
        print(f"⚠️ Error during Foot Locker scraping: {e}")
        return None

    finally:
        driver.quit()
