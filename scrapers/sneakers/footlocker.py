#!/usr/bin/env python3
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

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove for debugging
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    footlocker_deals = []

    try:
        driver.get(search_url)
        time.sleep(8)

        # Fetch product cards
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return footlocker_deals

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # Loop through first 3 product cards
        for index in range(min(3, len(product_cards))):
            try:
                print(f"\n🔄 Processing product [{index+1}]...")

                product_cards = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )
                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index+1}]: {product_url}")

                driver.get(product_url)
                time.sleep(8)

                # Open the 'Details' tab
                details_tab_xpath = "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"
                details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
                try:
                    details_panel = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, details_panel_xpath))
                    )
                    if "open" not in details_panel.get_attribute("class"):
                        details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                        driver.execute_script("arguments[0].click();", details_tab)
                        print("✅ Clicked on 'Details' section to ensure visibility for supplier SKU.")
                        time.sleep(2)
                except Exception:
                    print(f"⚠️ Could not open 'Details' tab for product [{index+1}]")

                # Get all colorway buttons
                colorway_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                )
                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{index+1}].")
                    colorway_buttons = [None]
                print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index+1}].")

                prev_sku = None  # Track previous SKU

                # Loop through each colorway
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        # Extract colorway product number
                        colorway_img = color_button.find_element(By.TAG_NAME, "img")
                        img_src = colorway_img.get_attribute("src")
                        product_number_match = re.search(r"/([A-Z0-9]+)\?", img_src)
                        colorway_product_number = product_number_match.group(1) if product_number_match else None

                        print(f"🔄 Extracted Foot Locker Product # [{index+1}], colorway [{color_index+1}]: {colorway_product_number}")

                        # Click the colorway thumbnail
                        driver.execute_script("arguments[0].click();", color_button)
                        print(f"✅ Clicked on colorway [{color_index+1}] for product [{index+1}].")

                        # Wait for the product number to update
                        WebDriverWait(driver, 10).until(
                            lambda d: colorway_product_number in d.find_element(By.XPATH, details_panel_xpath).text
                        )
                        time.sleep(2)  # Allow SKU to update

                        # Extract the SKU, ensuring it is different from the previous one
                        retries = 5
                        supplier_sku = None
                        while retries > 0:
                            details_text = driver.find_element(By.XPATH, details_panel_xpath).text
                            match = re.search(r"Supplier-sku #:\s*(\S+)", details_text)
                            if match:
                                new_sku = match.group(1)
                                if new_sku != prev_sku:
                                    supplier_sku = new_sku
                                    break
                            retries -= 1
                            time.sleep(2)

                        if not supplier_sku:
                            print(f"⚠️ Could not extract unique Supplier SKU for product [{index+1}], colorway [{color_index+1}]. Retrying details panel click.")
                            driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, details_tab_xpath))
                            time.sleep(3)
                            details_text = driver.find_element(By.XPATH, details_panel_xpath).text
                            match = re.search(r"Supplier-sku #:\s*(\S+)", details_text)
                            if match:
                                supplier_sku = match.group(1)

                        if supplier_sku:
                            print(f"✅ Extracted Supplier SKU for product [{index+1}], colorway [{color_index+1}]: {supplier_sku}")
                        else:
                            print(f"⚠️ Could not extract Supplier SKU for product [{index+1}], colorway [{color_index+1}].")
                            continue

                        # Store the extracted product number and supplier SKU
                        footlocker_deals.append({
                            "store": "Foot Locker",
                            "product_url": product_url,
                            "product_number": colorway_product_number,
                            "supplier_sku": supplier_sku
                        })
                        print(f"✅ Stored SKU: {supplier_sku} with Product # {colorway_product_number} for product [{index+1}], colorway [{color_index+1}].")

                        # Update previous SKU
                        prev_sku = supplier_sku

                    except Exception as e:
                        print(f"⚠️ Skipping colorway [{color_index+1}] for product [{index+1}] due to error: {e}")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Skipping product [{index+1}] due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals

if __name__ == "__main__":
    deals = get_footlocker_deals()
    print("\nFinal Foot Locker Deals:")
    for deal in deals:
        print(deal)
