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
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    footlocker_deals = []

    try:
        driver.get(search_url)
        time.sleep(5)

        # **Fetch all product cards**
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )

        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return footlocker_deals  

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # **Loop through first 3 product cards**
        for index in range(min(3, len(product_cards))):
            try:
                print(f"\n🔄 Processing product [{index + 1}]...")

                # **Re-fetch product cards to prevent stale elements**
                product_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )

                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index + 1}]: {product_url}")

                # **Extract the first colorway's product number from the URL**
                product_number_match = re.search(r'/product/[^/]+/([\w\d]+)\.html', product_url)
                product_number = product_number_match.group(1) if product_number_match else None

                if product_number:
                    print(f"🔄 Initial Foot Locker Product # [{index + 1}]: {product_number}")
                else:
                    print(f"⚠️ Could not extract initial Foot Locker Product # for product [{index + 1}].")

                # Visit product page
                driver.get(product_url)
                time.sleep(5)

                # **Find All Colorway Buttons**
                colorway_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                )

                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{index + 1}]. Extracting default style.")
                    colorway_buttons = [None]  

                print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index + 1}].")

                # **Loop through each colorway**
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        # **Extract Current Product Number Before Clicking**
                        previous_product_number = driver.execute_script(
                            "return document.getElementById('ProductDetails_hidden_styleSku')?.value || '';"
                        ).strip()
                        print(f"🔎 Before Clicking, Foot Locker Product # [{index + 1}], colorway [{color_index + 1}]: {previous_product_number}")

                        if color_button:
                            # **Ensure Button is Clickable**
                            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(color_button))

                            # **Force Click the Colorway Button multiple times using JavaScript**
                            driver.execute_script("arguments[0].dispatchEvent(new Event('mouseover', { bubbles: true }));", color_button)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('mousedown', { bubbles: true }));", color_button)
                            driver.execute_script("arguments[0].dispatchEvent(new Event('mouseup', { bubbles: true }));", color_button)
                            driver.execute_script("arguments[0].click();", color_button)

                            print(f"✅ Clicked on colorway [{color_index + 1}] for product [{index + 1}].")

                        # **Wait for Product # to Change**
                        max_attempts = 10
                        new_product_number = previous_product_number  # Start with the same value
                        while max_attempts > 0:
                            time.sleep(1)  # Wait before checking

                            new_product_number = driver.execute_script(
                                "return document.getElementById('ProductDetails_hidden_styleSku')?.value || '';"
                            ).strip()

                            if new_product_number and new_product_number != previous_product_number:
                                print(f"🔄 Updated Foot Locker Product # [{index + 1}], colorway [{color_index + 1}]: {new_product_number}")
                                break  # Exit loop once Product # updates

                            max_attempts -= 1
                            print(f"⏳ Waiting for Product # update for product [{index + 1}], colorway [{color_index + 1}]...")

                        if not new_product_number or new_product_number == previous_product_number:
                            print(f"⚠️ Could not extract updated Foot Locker Product # for product [{index + 1}], colorway [{color_index + 1}]. Skipping.")
                            continue  # Move to next colorway

                        # **Ensure "Details" tab is open**
                        try:
                            details_tab = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"))
                            )
                            driver.execute_script("arguments[0].click();", details_tab)
                            print(f"✅ Clicked on 'Details' section for product [{index + 1}], colorway [{color_index + 1}].")
                            time.sleep(2)
                        except:
                            print(f"⚠️ Could not open 'Details' tab for product [{index + 1}], colorway [{color_index + 1}].")

                        # **Extract Foot Locker Supplier SKU**
                        supplier_skus = []
                        try:
                            sku_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Supplier-sku #:')]/following-sibling::span")
                            for elem in sku_elements:
                                sku = elem.text.strip()
                                if sku:
                                    supplier_skus.append(sku)

                        except:
                            print(f"⚠️ Supplier SKUs not found in page elements for product [{index + 1}], colorway [{color_index + 1}].")

                        # **Fallback: Extract from Page Source**
                        if not supplier_skus:
                            page_source = driver.page_source
                            matches = re.findall(r'Supplier-sku #:\s*<!-- -->\s*([\w\d-]+)', page_source)

                            if matches:
                                supplier_skus = list(set(matches))
                                print(f"✅ Extracted Foot Locker Supplier SKUs from Page Source [{index + 1}], colorway [{color_index + 1}]: {supplier_skus}")
                            else:
                                print(f"❌ Supplier SKUs not found for product [{index + 1}], colorway [{color_index + 1}].")

                        # **Store Results**
                        if new_product_number and supplier_skus:
                            for sku in supplier_skus:
                                footlocker_deals.append({
                                    "store": "Foot Locker",
                                    "product_url": product_url,
                                    "product_number": new_product_number,
                                    "supplier_sku": sku
                                })
                                print(f"✅ Stored SKU: {sku} with Product # {new_product_number} for product [{index + 1}], colorway [{color_index + 1}].")

                    except Exception as e:
                        print(f"⚠️ Skipping colorway [{color_index + 1}] for product [{index + 1}] due to error: {e}")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Skipping product [{index + 1}] due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals
