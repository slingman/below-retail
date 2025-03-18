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
                print(f"✅ Extracted Foot Locker Product URL: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Ensure full page load

                # Extract Foot Locker Product Number from URL
                product_number_match = re.search(r'/product/[^/]+/([\w\d]+)\.html', product_url)
                product_number = product_number_match.group(1) if product_number_match else None

                # **Corrected Foot Locker Product URL**
                if product_number:
                    correct_product_url = f"https://www.footlocker.com/product/~/ {product_number}.html".replace(" ~/ ", "~/").strip()
                    print(f"✅ Corrected Foot Locker Product URL: {correct_product_url}")
                else:
                    print("⚠️ Could not extract Foot Locker Product # for URL.")

                # **Extract Supplier SKU from Page Elements**
                supplier_sku = None
                potential_sku_xpaths = [
                    "//span[contains(text(), 'Supplier Sku')]/following-sibling::span",
                    "//p[contains(text(), 'Supplier Sku')]/following-sibling::p",
                    "//li[contains(text(), 'Supplier Sku')]/following-sibling::li"
                ]

                for xpath in potential_sku_xpaths:
                    try:
                        supplier_sku_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        supplier_sku = supplier_sku_element.text.strip()
                        if supplier_sku:
                            print(f"✅ Extracted Foot Locker Supplier SKU from elements: {supplier_sku}")
                            break  # Exit loop once found
                    except:
                        continue  # Try the next XPath if one fails

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
                    print(f"✅ Extracted Foot Locker Supplier SKU #: {supplier_sku}")
                else:
                    print("⚠️ Supplier SKU not found.")

                return  # Stop after first product for debugging

            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    finally:
        driver.quit()
