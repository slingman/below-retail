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

        # Get first product card
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")
        if not product_cards:
            print("⚠️ No products found on Foot Locker search page.")
            return None
        
        first_product = product_cards[0]

        # Extract Correct Product URL
        product_link_element = first_product.find_element(By.CLASS_NAME, "ProductCard-link")
        product_url = product_link_element.get_attribute("href")
        print(f"✅ Extracted Foot Locker Product URL: {product_url}")

        # Visit product page
        driver.get(product_url)

        # Wait for full page load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        time.sleep(3)  # Small buffer to avoid stale elements
        
        # Extract SKU
        page_source = driver.page_source

        # Look for SKU using regex (to match different formats)
        sku_match = re.search(r"Supplier-sku\s*#:\s*([\w-]+)", page_source)
        if sku_match:
            supplier_sku = sku_match.group(1).strip()
            print(f"✅ Extracted Foot Locker Supplier-sku #: {supplier_sku}")
        else:
            print("⚠️ Could not find Supplier-sku # on Foot Locker page.")
            supplier_sku = None

        # Return extracted product details
        return {
            "store": "Foot Locker",
            "product_url": product_url,
            "supplier_sku": supplier_sku
        }

    except Exception as e:
        print(f"⚠️ Error during Foot Locker scraping: {e}")
        return None

    finally:
        driver.quit()
