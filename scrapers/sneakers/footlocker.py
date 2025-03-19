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

    # **Set up WebDriver**
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove for debugging
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    footlocker_deals = []

    try:
        driver.get(search_url)
        time.sleep(5)

        # **Fetch product cards**
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

                # **Re-fetch product cards to avoid stale elements**
                product_cards = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )

                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index + 1}]: {product_url}")

                # **Visit the product page**
                driver.get(product_url)
                time.sleep(5)

                # **Ensure 'Details' tab is open initially**
                details_tab_xpath = "//button[contains(@id, 'ProductDetails-tabs-details-tab')]"
                details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
                try:
                    details_panel = driver.find_element(By.XPATH, details_panel_xpath)
                    if "open" not in details_panel.get_attribute("class"):
                        details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                        driver.execute_script("arguments[0].click();", details_tab)
                        print(f"✅ Clicked on 'Details' section to ensure visibility for supplier SKU.")
                        time.sleep(2)
                    else:
                        print(f"🔄 'Details' tab is already open.")
                except Exception as e:
                    print(f"⚠️ Could not open 'Details' tab initially for product [{index + 1}]: {e}")

                # **Extract all colorway buttons**
                colorway_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                )

                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{index + 1}]. Using default style.")
                    colorway_buttons = [None]

                print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index + 1}].")

                # **Loop through each colorway**
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        # **Extract colorway product number from thumbnail image URL**
                        colorway_img = color_button.find_element(By.TAG_NAME, "img")
                        img_src = colorway_img.get_attribute("src")
                        product_number_match = re.search(r"/([A-Z0-9]+)\?", img_src)
                        colorway_product_number = product_number_match.group(1) if product_number_match else None

                        if not colorway_product_number:
                            print(f"⚠️ Could not extract Foot Locker Product # for colorway [{color_index + 1}]. Skipping.")
                            continue

                        print(f"🔄 Extracted Foot Locker Product # [{index + 1}], colorway [{color_index + 1}]: {colorway_product_number}")

                        # **Click on the colorway button**
                        driver.execute_script("arguments[0].click();", color_button)
                        print(f"✅ Clicked on colorway [{color_index + 1}] for product [{index + 1}].")
                        time.sleep(3)  # Allow page to update

                        # After clicking the colorway, wait until the details panel shows the new product #
                        try:
                            WebDriverWait(driver, 10).until(
                                lambda d: colorway_product_number in d.find_element(By.XPATH, details_panel_xpath).text
                            )
                            print(f"🔄 Detected updated product number in 'Details' panel for colorway [{color_index + 1}].")
                        except Exception as wait_err:
                            print(f"⚠️ Timeout waiting for 'Details' update for colorway [{color_index + 1}]: {wait_err}")
                            continue

                        # **Ensure 'Details' tab is still open**
                        try:
                            details_panel = driver.find_element(By.XPATH, details_panel_xpath)
                            if "open" not in details_panel.get_attribute("class"):
                                details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                                driver.execute_script("arguments[0].click();", details_tab)
                                print(f"✅ Clicked on 'Details' tab again after selecting colorway [{color_index + 1}].")
                                time.sleep(2)
                            else:
                                print(f"🔄 'Details' tab is already open for colorway [{color_index + 1}].")
                        except Exception as e:
                            print(f"⚠️ Could not ensure 'Details' tab is open for colorway [{color_index + 1}]: {e}")

                        # **Scroll to details panel**
                        driver.execute_script("arguments[0].scrollIntoView();", details_panel)
                        time.sleep(1)

                        # **Extract Supplier SKU from the details panel text using regex**
                        supplier_sku = None
                        details_text = details_panel.text
                        # Use regex to extract supplier SKU (adjust pattern as needed)
                        sku_match = re.search(r"Supplier-sku #:\s*([A-Z0-9-]+)", details_text)
                        if sku_match:
                            supplier_sku = sku_match.group(1).strip()

                        if supplier_sku:
                            print(f"✅ Extracted Supplier SKU for product [{index + 1}], colorway [{color_index + 1}]: {supplier_sku}")
                        else:
                            print(f"⚠️ Could not extract Supplier SKU for product [{index + 1}], colorway [{color_index + 1}].")

                        # **Store results if both product number and supplier SKU were obtained**
                        if colorway_product_number and supplier_sku:
                            footlocker_deals.append({
                                "store": "Foot Locker",
                                "product_url": product_url,
                                "product_number": colorway_product_number,
                                "supplier_sku": supplier_sku
                            })
                            print(f"✅ Stored SKU: {supplier_sku} with Product # {colorway_product_number} for product [{index + 1}], colorway [{color_index + 1}].")

                    except Exception as ce:
                        print(f"⚠️ Skipping colorway [{color_index + 1}] for product [{index + 1}] due to error: {ce}")

                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Skipping product [{index + 1}] due to error: {e}")

    finally:
        driver.quit()

    return footlocker_deals
