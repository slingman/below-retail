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

    footlocker_deals = []

    try:
        driver.get(search_url)
        time.sleep(5)  # Allow page to load

        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for i, card in enumerate(product_cards[:3]):  # Limit to 3 styles for now
            try:
                # Extract Product URL from search results
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Ensure full page load

                # **Click 'Details' section to reveal Supplier SKU**
                try:
                    details_tab = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"))
                    )
                    driver.execute_script("arguments[0].click();", details_tab)
                    print("✅ Clicked on 'Details' section to reveal Supplier SKU.")
                    time.sleep(3)  # Allow content to expand
                except:
                    print("⚠️ 'Details' section not found or could not be clicked.")

                # **Extract Supplier SKU from Page Source**
                supplier_sku = None
                page_source = driver.page_source
                match = re.search(r'Supplier-sku #:\s*<!-- -->\s*([\w\d-]+)', page_source)
                if match:
                    supplier_sku = match.group(1).strip()
                    print(f"✅ Extracted Foot Locker Supplier SKU: {supplier_sku}")
                else:
                    print("❌ Supplier SKU not found.")

                # **Store the deal data**
                if supplier_sku:
                    footlocker_deals.append({
                        "store": "Foot Locker",
                        "product_url": product_url,
                        "supplier_sku": supplier_sku
                    })

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals
