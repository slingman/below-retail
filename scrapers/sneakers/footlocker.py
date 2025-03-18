from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

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

                # Extract Supplier-sku #
                details_section = driver.find_element(By.XPATH, "//div[contains(text(), 'Supplier-sku #:')]")
                supplier_sku = details_section.text.split("Supplier-sku #:")[-1].strip()
                print(f"✅ Extracted Foot Locker Supplier-sku #: {supplier_sku}")

                # Return after first product for debugging
                return

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
