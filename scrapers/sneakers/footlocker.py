#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_details_text(driver, xpath):
    try:
        element = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        text = element.text
        if not text:
            text = element.get_attribute("innerText")
        return text
    except Exception as e:
        print(f"⚠️ Error getting details text: {e}")
        return ""

def get_supplier_sku(driver, supplier_xpath):
    try:
        # Get the text from the supplier SKU element
        supplier_text = driver.find_element(By.XPATH, supplier_xpath).text
        # Expecting text like "Supplier-sku #: FB9660-002"
        parts = supplier_text.split(":", 1)
        if len(parts) > 1:
            return parts[1].strip()
        return supplier_text.strip()
    except Exception as e:
        print(f"⚠️ Error extracting supplier SKU: {e}")
        return ""

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
    # This is the XPath to the details panel and to the supplier SKU span within it.
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    supplier_sku_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"

    try:
        driver.get(search_url)
        time.sleep(8)
        
        # Handle cookie consent if present
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]"))
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")
        
        # Fetch product cards
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return footlocker_deals

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # Process first 3 product cards
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

                # Get product title
                try:
                    product_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text
                    print(f"📝 Product Title: {product_title}")
                except Exception:
                    product_title = f"Product {index+1}"
                    print(f"⚠️ Could not extract product title, using '{product_title}'")

                # Open details section
                try:
                    details_panel = driver.find_element(By.XPATH, details_panel_xpath)
                    if "open" not in details_panel.get_attribute("class"):
                        try:
                            details_tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                            driver.execute_script("arguments[0].click();", details_tab)
                            print("✅ Clicked on 'Details' section to open it")
                            time.sleep(3)
                        except Exception:
                            print("⚠️ Could not click details tab; proceeding anyway")
                    else:
                        print("🔄 'Details' section is already open")
                except Exception:
                    print("⚠️ Details panel not found; proceeding anyway")
                time.sleep(3)
                
                # Get colorway buttons using multiple selectors
                colorway_selectors = [
                    (By.CLASS_NAME, "ColorwayStyles-field"),
                    (By.XPATH, "//div[contains(@class, 'ColorwaySelector')]//div[contains(@class, 'ColorwayStyles-field')]"),
                    (By.XPATH, "//div[contains(@class, 'ColorwaySelector')]//img[@alt]")
                ]
                colorway_buttons = []
                for selector_type, selector in colorway_selectors:
                    try:
                        colorway_buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((selector_type, selector))
                        )
                        if colorway_buttons:
                            print(f"✅ Found colorway buttons using selector: {selector}")
                            break
                    except Exception:
                        continue
                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{index+1}]. Using default style.")
                    colorway_buttons = [None]
                else:
                    print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index+1}].")
                
                previous_supplier_sku = None  # For tracking changes
                
                # Process each colorway
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {product_title}...")
                        if color_button is not None:
                            try:
                                colorway_img = color_button.find_element(By.TAG_NAME, "img")
                                img_src = colorway_img.get_attribute("src")
                                product_number_patterns = [
                                    r"/([A-Z0-9]{6,10})\?",
                                    r"_([A-Z0-9]{6,10})_",
                                    r"-([A-Z0-9]{6,10})-"
                                ]
                                colorway_product_number = None
                                for pattern in product_number_patterns:
                                    match = re.search(pattern, img_src)
                                    if match:
                                        colorway_product_number = match.group(1)
                                        break
                            except Exception as e:
                                print(f"⚠️ Error extracting product number from image: {e}")
                                traceback.print_exc()
                                colorway_product_number = f"UNKNOWN-{color_index+1}"
                            
                            if not colorway_product_number:
                                print(f"⚠️ Could not extract product number for colorway [{color_index+1}], using index.")
                                colorway_product_number = f"UNKNOWN-{color_index+1}"
                            print(f"🔄 Colorway Product #: {colorway_product_number}")
                            
                            # Click the colorway thumbnail using ActionChains
                            try:
                                actions = ActionChains(driver)
                                actions.move_to_element(color_button).click().perform()
                                print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
                            except Exception as e:
                                print(f"⚠️ ActionChains click failed: {e}")
                                driver.execute_script("arguments[0].click();", color_button)
                                print(f"✅ Clicked on colorway [{color_index+1}] using JavaScript fallback")
                            
                            # Wait for the details panel to update; increase delay to 15 seconds
                            time.sleep(15)
                        else:
                            colorway_product_number = "DEFAULT"
                            print("ℹ️ Processing default colorway only")
                        
                        # Now, specifically get the supplier SKU text from the second span within the details panel
                        try:
                            supplier_sku_text = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[2]").text
                            supplier_sku = supplier_sku_text.split(":", 1)[-1].strip()
                            print(f"✅ Extracted Supplier SKU from span: {supplier_sku}")
                        except Exception as e:
                            print(f"⚠️ Error extracting supplier SKU from span: {e}")
                            supplier_sku = None
                        
                        if not supplier_sku:
                            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}]")
                            continue
                        
                        # Optionally, if you want to force a re-read if the supplier SKU hasn't changed,
                        # you could compare to previous_supplier_sku and wait longer, but in this version we simply read it.
                        previous_supplier_sku = supplier_sku
                        
                        screenshot_path = f"footlocker_product_{index+1}_colorway_{color_index+1}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print(f"📷 Saved screenshot to {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to save screenshot: {e}")
                        
                        footlocker_deals.append({
                            "store": "Foot Locker",
                            "product_title": product_title,
                            "product_url": product_url,
                            "product_number": colorway_product_number,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_index + 1
                        })
                        print(f"✅ Stored SKU: {supplier_sku} with Product # {colorway_product_number}")
                    
                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_index+1}]: {e}")
                        traceback.print_exc()
                        
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error processing product [{index+1}]: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"⚠️ Main process error: {e}")
        traceback.print_exc()
    finally:
        driver.quit()
    
    print("\n📊 SUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(footlocker_deals)}")
    
    return footlocker_deals

if __name__ == "__main__":
    print("🏃 Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\n🏁 Final Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']})")
