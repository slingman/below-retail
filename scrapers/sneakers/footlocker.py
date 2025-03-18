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

        product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

        for card in product_cards:
            try:
                # Extract Product URL from search results
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")

                # Extract Foot Locker Product Number from URL
                product_number_match = re.search(r'/product/[^/]+/([\w\d]+)\.html', product_url)
                product_number = product_number_match.group(1) if product_number_match else None

                # **Ensure Correct Foot Locker Product URL Format**
                if product_number:
                    corrected_product_url = f"https://www.footlocker.com/product/~/Z{product_number}.html"
                    print(f"✅ Corrected Foot Locker Product URL: {corrected_product_url}")
                else:
                    corrected_product_url = product_url  # Fallback to original
                    print(f"⚠️ Could not extract Foot Locker Product #, using original URL: {product_url}")

                # Visit the product page
                driver.get(corrected_product_url)
                time.sleep(5)  # Ensure full page load

                # **Try Clicking the "Details" Section to Reveal SKU**
                try:
                    details_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Details')]"))
                    )
                    details_button.click()
                    time.sleep(2)  # Allow details section to expand
                    print("✅ Clicked 'Details' section to reveal SKU.")
                except Exception:
                    print("⚠️ 'Details' section not found or could not be clicked.")

                # **Extract Supplier SKU from Page Elements**
                supplier_sku = None
                try:
                    supplier_sku_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Supplier Sku')]/following-sibling::span"))
                    )
                    supplier_sku = supplier_sku_element.text.strip()
                    print(f"✅ Extracted Foot Locker Supplier SKU from elements: {supplier_sku}")
                except:
                    print("⚠️ Supplier SKU not found in page elements. Checking page source...")

                # **Fallback: Extract Supplier SKU from Page Source (if missing)**
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
                    print(f"✅ Final Extracted Foot Locker Supplier SKU #: {supplier_sku}")
                else:
                    print("❌ Supplier SKU still not found.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
