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

    # ✅ Using last **stable** ChromeDriver setup
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

        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product URL from search results
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # ✅ No need to modify the URL; Foot Locker redirects correctly
                driver.get(product_url)
                time.sleep(5)  # Ensure full page load

                # **Click on 'Details' section**
                try:
                    details_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.ID, "ProductDetails-tabs-details-tab-0"))
                    )
                    driver.execute_script("arguments[0].click();", details_button)
                    print("✅ Clicked on 'Details' section to reveal Supplier SKU.")
                    time.sleep(3)  # Allow content to expand
                except Exception:
                    print("⚠️ 'Details' section not found or could not be clicked.")

                # **Extract Supplier SKUs**
                supplier_skus = set()  # Store unique SKUs
                try:
                    sku_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Supplier-sku')]/following-sibling::span")
                    for sku_element in sku_elements:
                        sku = sku_element.text.strip()
                        supplier_skus.add(sku)
                except Exception:
                    print("⚠️ Supplier SKU not found in page elements. Checking page source...")

                # **Fallback: Extract from Page Source**
                if not supplier_skus:
                    page_source = driver.page_source
                    matches = re.findall(r'Supplier-sku\s*#:\s*<!-- -->\s*([\w\d-]+)', page_source)
                    if matches:
                        supplier_skus.update(matches)

                if supplier_skus:
                    print(f"✅ Extracted Foot Locker Supplier SKUs: {', '.join(supplier_skus)}")
                else:
                    print("❌ Supplier SKUs still not found.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
