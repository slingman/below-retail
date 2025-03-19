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

    # Set up Selenium WebDriver (Stable ChromeDriver Version)
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

        # **Fetch all product cards on the search page**
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )

        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return footlocker_deals  # Return empty list if no products are found

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # **Loop through multiple product cards**
        for index in range(min(3, len(product_cards))):  # Only checking first 3 products
            try:
                print(f"\n🔄 Processing product [{index + 1}]...")

                # **Re-fetch product cards before interacting (to prevent stale elements)**
                product_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )

                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index + 1}]: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(5)  # Allow full page load

                # **Find All Available Styles (Colorways)**
                colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")

                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{index + 1}]. Extracting default style.")
                    colorway_buttons = [None]  # Default to the current selected style

                print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index + 1}].")

                # **Loop through each available colorway**
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        if color_button:
                            driver.execute_script("arguments[0].click();", color_button)
                            print(f"✅ Selected colorway [{color_index + 1}] for product [{index + 1}].")
                            time.sleep(3)  # Allow UI update

                        # **Click 'Details' section to reveal Supplier SKU**
                        try:
                            details_tab = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"))
                            )
                            driver.execute_script("arguments[0].click();", details_tab)
                            print(f"✅ Clicked on 'Details' section for product [{index + 1}], colorway [{color_index + 1}].")
                            time.sleep(3)  # Allow content to expand
                        except Exception as e:
                            print(f"⚠️ 'Details' section not found for product [{index + 1}], colorway [{color_index + 1}]: {e}")
                            continue  # Skip to the next colorway

                        # **Extract All Available Supplier SKUs**
                        supplier_skus = []
                        try:
                            sku_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Supplier-sku #:')]/following-sibling::span")
                            for elem in sku_elements:
                                sku = elem.text.strip()
                                if sku:
                                    supplier_skus.append(sku)

                        except Exception as e:
                            print(f"⚠️ Supplier SKUs not found in page elements for product [{index + 1}], colorway [{color_index + 1}]: {e}")
                            print("🛠️ Attempting fallback extraction from page source...")

                        # **Fallback: Extract from Page Source**
                        if not supplier_skus:
                            page_source = driver.page_source
                            matches = re.findall(r'Supplier-sku #:\s*<!-- -->\s*([\w\d-]+)', page_source)

                            if matches:
                                supplier_skus = list(set(matches))  # Remove duplicates
                                print(f"✅ Extracted Foot Locker Supplier SKUs from Page Source [{index + 1}], colorway [{color_index + 1}]: {supplier_skus}")
                            else:
                                print(f"❌ Supplier SKUs not found for product [{index + 1}], colorway [{color_index + 1}].")

                        # **Store the extracted SKUs**
                        for sku in supplier_skus:
                            footlocker_deals.append({
                                "store": "Foot Locker",
                                "product_url": product_url,
                                "supplier_sku": sku
                            })

                    except Exception as e:
                        print(f"⚠️ Skipping colorway [{color_index + 1}] for product [{index + 1}] due to error: {e}")

                # **Introduce a short pause between processing each product**
                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Skipping product [{index + 1}] due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals
