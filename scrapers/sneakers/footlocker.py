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

        # **Get all product cards on the search page**
        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return footlocker_deals  # Return empty if no products are found

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # **Loop through multiple product cards**
        for index, card in enumerate(product_cards[:3]):  # Only checking 3 products for now
            try:
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index + 1}]: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Allow full page load

                # **Click 'Details' section to reveal Supplier SKU**
                try:
                    details_tab = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"))
                    )
                    driver.execute_script("arguments[0].click();", details_tab)
                    print(f"✅ Clicked on 'Details' section for product [{index + 1}].")
                    time.sleep(3)  # Allow content to expand
                except:
                    print(f"⚠️ 'Details' section not found for product [{index + 1}].")

                # **Extract All Available Styles**
                supplier_skus = []
                try:
                    sku_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Supplier-sku #:')]/following-sibling::span")
                    for elem in sku_elements:
                        sku = elem.text.strip()
                        if sku:
                            supplier_skus.append(sku)

                except:
                    print(f"⚠️ Supplier SKUs not found in page elements for product [{index + 1}]. Checking page source...")

                # **Fallback: Extract from Page Source**
                if not supplier_skus:
                    page_source = driver.page_source
                    matches = re.findall(r'Supplier-sku #:\s*<!-- -->\s*([\w\d-]+)', page_source)

                    if matches:
                        supplier_skus = list(set(matches))  # Remove duplicates
                        print(f"✅ Extracted Foot Locker Supplier SKUs from Page Source [{index + 1}]: {supplier_skus}")
                    else:
                        print(f"❌ Supplier SKUs not found for product [{index + 1}].")

                # **Store the extracted SKUs**
                for sku in supplier_skus:
                    footlocker_deals.append({
                        "store": "Foot Locker",
                        "product_url": product_url,
                        "supplier_sku": sku
                    })

            except Exception as e:
                print(f"⚠️ Skipping a product [{index + 1}] due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals
