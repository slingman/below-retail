from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import json

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
        time.sleep(5)  # Allow time for page load

        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product URL from search results
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Ensure full page load

                # Extract Product Number from URL
                product_number_match = re.search(r'/product/[^/]+/([\w\d]+)\.html', product_url)
                product_number = product_number_match.group(1) if product_number_match else None

                # **Correct Foot Locker Product URL Format**
                if product_number:
                    correct_product_url = f"https://www.footlocker.com/product/~/ {product_number}.html".replace("~/ ", "").strip()
                    print(f"✅ Corrected Foot Locker Product URL: {correct_product_url}")
                else:
                    print("⚠️ Could not extract Foot Locker Product # for URL.")

                # **Approach 1: Extract Supplier SKU from JavaScript Object**
                try:
                    script = "return window.__PRELOADED_STATE__ ? JSON.stringify(window.__PRELOADED_STATE__) : '';"
                    json_data = driver.execute_script(script)
                    if json_data:
                        data = json.loads(json_data)
                        supplier_sku = data.get("ProductDetails", {}).get("currentProduct", {}).get("sku")
                        if supplier_sku:
                            print(f"✅ Extracted Foot Locker Supplier SKU from JavaScript: {supplier_sku}")
                        else:
                            print("⚠️ Supplier SKU not found in JavaScript.")
                    else:
                        print("⚠️ No JavaScript data found.")
                except Exception as e:
                    print(f"⚠️ JavaScript extraction error: {e}")
                    supplier_sku = None

                # **Approach 2: Search for Supplier SKU in Page Source (Fallback)**
                if not supplier_sku:
                    page_source = driver.page_source
                    match = re.search(r'"supplierSku"\s*:\s*"([\w\d-]+)"', page_source)
                    if match:
                        supplier_sku = match.group(1).strip()
                        print(f"✅ Extracted Foot Locker Supplier SKU from Page Source: {supplier_sku}")
                    else:
                        print("⚠️ Supplier SKU not found in Page Source.")

                # **Final Output**
                if supplier_sku:
                    print(f"✅ Final Supplier SKU: {supplier_sku}")
                else:
                    print("⚠️ Supplier SKU extraction failed.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
