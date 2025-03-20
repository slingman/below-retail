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
    # Add user agent to appear more like a regular browser
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    # Set a larger window size for better rendering
    driver.set_window_size(1920, 1080)

    footlocker_deals = []

    try:
        driver.get(search_url)
        # Increased initial wait time to ensure page loads completely
        time.sleep(8)
        
        # Check for cookie consent or popup and handle if present
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

        # Loop through first 3 product cards
        for index in range(min(3, len(product_cards))):
            try:
                print(f"\n🔄 Processing product [{index+1}]...")

                # Re-fetch product cards to avoid stale elements
                product_cards = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )
                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index+1}]: {product_url}")

                # Visit the product page
                driver.get(product_url)
                # Increased wait time to ensure product page fully loads
                time.sleep(8)

                # Get product title for reference
                try:
                    product_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text
                    print(f"📝 Product Title: {product_title}")
                except Exception:
                    product_title = f"Product {index+1}"
                    print(f"⚠️ Could not extract product title, using '{product_title}'")

                # Try to locate the details section regardless of tab structure
                details_selectors = [
                    "//button[contains(@id, 'ProductDetails-tabs-details-tab')]",  # Standard details tab
                    "//button[contains(text(), 'Details')]",  # Text-based selector
                    "//div[contains(@class, 'ProductDetails-description')]"  # Direct access to description
                ]
                
                details_found = False
                for selector in details_selectors:
                    try:
                        details_element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        driver.execute_script("arguments[0].click();", details_element)
                        print(f"✅ Found and clicked 'Details' section using selector: {selector}")
                        details_found = True
                        time.sleep(3)  # Wait for details to expand
                        break
                    except Exception:
                        continue
                
                if not details_found:
                    print("⚠️ Could not find Details section using standard selectors. Proceeding anyway.")

                # Wait for page to stabilize
                time.sleep(3)
                
                # Get all colorway buttons with improved selector strategy
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
                    print(f"⚠️ No colorways found for product [{index+1}]. Extracting default style only.")
                    # Create a mock list with None to process default colorway
                    colorway_buttons = [None]
                else:
                    print(f"🎨 Found {len(colorway_buttons)} colorways for product [{index+1}].")
                
                # Reset for each product
                processed_skus = set()

                # Loop through each colorway
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {product_title}...")
                        
                        # Skip if we only have a default colorway (None)
                        if color_button is not None:
                            # Extract the product number from the colorway's image URL
                            try:
                                colorway_img = color_button.find_element(By.TAG_NAME, "img")
                                img_src = colorway_img.get_attribute("src")
                                # Different regex patterns to match product numbers
                                product_number_patterns = [
                                    r"/([A-Z0-9]{6,10})\?",  # Standard format
                                    r"_([A-Z0-9]{6,10})_",   # Alternate format
                                    r"-([A-Z0-9]{6,10})-"    # Another alternate format
                                ]
                                
                                colorway_product_number = None
                                for pattern in product_number_patterns:
                                    match = re.search(pattern, img_src)
                                    if match:
                                        colorway_product_number = match.group(1)
                                        break
                                        
                            except Exception as e:
                                print(f"⚠️ Error extracting product number from image: {e}")
                                colorway_product_number = f"UNKNOWN-{color_index+1}"
                            
                            if not colorway_product_number:
                                print(f"⚠️ Could not extract Foot Locker Product # for colorway [{color_index+1}]. Using index.")
                                colorway_product_number = f"UNKNOWN-{color_index+1}"

                            print(f"🔄 Colorway Product #: {colorway_product_number}")

                            # Click the colorway thumbnail with retry mechanism
                            max_attempts = 3
                            for attempt in range(max_attempts):
                                try:
                                    # Use JavaScript click which is more reliable
                                    driver.execute_script("arguments[0].click();", color_button)
                                    print(f"✅ Clicked on colorway [{color_index+1}] (Attempt {attempt+1})")
                                    # Wait for page to update
                                    time.sleep(5)
                                    break
                                except Exception as e:
                                    print(f"⚠️ Click attempt {attempt+1} failed: {e}")
                                    if attempt == max_attempts - 1:
                                        raise Exception("Failed to click colorway after multiple attempts")
                                    time.sleep(2)
                        else:
                            # Default colorway case
                            colorway_product_number = "DEFAULT"
                            print("ℹ️ Processing default colorway only")
                        
                        # Scroll to make sure details are visible
                        try:
                            # Look for details panel with multiple possible selectors
                            details_panel_selectors = [
                                "//div[@id='ProductDetails-tabs-details-panel']",
                                "//div[contains(@class, 'ProductDetails-description')]",
                                "//div[contains(text(), 'Supplier-sku #:')]/..",
                                "//div[contains(text(), 'Supplier-sku')]/.."
                            ]
                            
                            details_panel = None
                            for selector in details_panel_selectors:
                                try:
                                    details_panel = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located((By.XPATH, selector))
                                    )
                                    if details_panel:
                                        break
                                except Exception:
                                    continue
                                    
                            if details_panel:
                                # Scroll the panel into view
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", details_panel)
                                print("✅ Found and scrolled to details panel")
                                time.sleep(2)  # Wait for any animations to complete
                            else:
                                print("⚠️ Could not find details panel with standard selectors")
                                
                        except Exception as e:
                            print(f"⚠️ Error scrolling to details panel: {e}")
                        
                        # Get all text from the product page to search for SKU
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        
                        # Try multiple patterns to find the supplier SKU
                        sku_patterns = [
                            r"Supplier-sku #:\s*(\S+)",     # Standard format
                            r"Supplier[-\s]sku:?\s*(\S+)",  # Alternative format
                            r"Item #:\s*(\S+)",            # Another possible format
                            r"Style #:\s*(\S+)",           # Yet another format
                            r"Style:?\s*(\S+)",           # Simplified format
                        ]
                        
                        supplier_sku = None
                        for pattern in sku_patterns:
                            match = re.search(pattern, page_text, re.IGNORECASE)
                            if match:
                                supplier_sku = match.group(1).strip()
                                print(f"✅ Found Supplier SKU using pattern: {pattern}")
                                break
                                
                        if not supplier_sku:
                            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}]")
                            continue
                            
                        # Check if we've already processed this SKU
                        if supplier_sku in processed_skus:
                            print(f"⚠️ Duplicate SKU detected: {supplier_sku}. Skipping.")
                            continue
                            
                        processed_skus.add(supplier_sku)
                        print(f"✅ Extracted Supplier SKU: {supplier_sku}")
                        
                        # Take a screenshot for reference (helpful for debugging)
                        screenshot_path = f"footlocker_product_{index+1}_colorway_{color_index+1}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print(f"📷 Saved screenshot to {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to save screenshot: {e}")

                        # Save the extracted product number and supplier SKU into the results list
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
                        
                # Sleep between products to avoid rate limiting
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error processing product [{index+1}]: {e}")

    except Exception as e:
        print(f"⚠️ Main process error: {e}")
    finally:
        driver.quit()

    # Print summary of results
    print("\n📊 SUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(footlocker_deals)}")
    
    return footlocker_deals

if __name__ == "__main__":
    print("🏃 Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\n🏁 Final Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']})")
