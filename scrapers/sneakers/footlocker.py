#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import random

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    # Set up WebDriver with more realistic browser settings
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Remove for debugging
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Use a realistic user agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    # Additional settings to make browser more realistic
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=service, options=options)
    # Execute JS to make navigator.webdriver undefined
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    footlocker_deals = []

    try:
        driver.get(search_url)
        # Random wait to appear more human-like
        time.sleep(random.uniform(7, 10))
        
        # Handle cookie popup if present
        try:
            cookie_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]")
            if cookie_buttons:
                cookie_buttons[0].click()
                print("✅ Clicked on cookie accept button")
                time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"ℹ️ No cookie consent dialog found or couldn't be closed: {e}")

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

                # Go back to search results page if we're not on it
                if not driver.current_url.startswith(search_url):
                    driver.get(search_url)
                    time.sleep(random.uniform(5, 8))
                
                # Re-fetch product cards to avoid stale elements
                product_cards = WebDriverWait(driver, 15).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
                )
                
                # Get product URL from card
                card = product_cards[index]
                product_url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                print(f"✅ Extracted Foot Locker Product URL [{index+1}]: {product_url}")

                # Visit the product page
                driver.get(product_url)
                time.sleep(random.uniform(7, 10))  # Randomized wait time

                # Get product title
                try:
                    product_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text
                    print(f"📝 Product Title: {product_title}")
                except Exception:
                    product_title = f"Product {index+1}"
                    print(f"⚠️ Could not extract product title, using '{product_title}'")

                # Try to locate and click the details tab
                details_selectors = [
                    "//button[contains(@id, 'ProductDetails-tabs-details-tab')]",
                    "//button[contains(text(), 'Details')]",
                    "//div[contains(@class, 'ProductDetails')]//button[contains(text(), 'Details')]"
                ]
                
                details_found = False
                for selector in details_selectors:
                    try:
                        details_element = WebDriverWait(driver, 8).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        # Multiple attempts to ensure click works
                        for attempt in range(3):
                            try:
                                # Try different click methods
                                if attempt == 0:
                                    details_element.click()
                                elif attempt == 1:
                                    driver.execute_script("arguments[0].click();", details_element)
                                else:
                                    ActionChains(driver).move_to_element(details_element).click().perform()
                                print(f"✅ Clicked 'Details' section (Attempt {attempt+1})")
                                details_found = True
                                time.sleep(random.uniform(2, 4))
                                break
                            except Exception as e:
                                print(f"⚠️ Click attempt {attempt+1} failed: {e}")
                                time.sleep(1)
                        
                        if details_found:
                            break
                    except Exception:
                        continue
                
                if not details_found:
                    print("⚠️ Could not click Details tab. Will try to find SKU info anyway.")

                # Get all colorway buttons
                colorway_selectors = [
                    (By.CLASS_NAME, "ColorwayStyles-field"),
                    (By.XPATH, "//div[contains(@class, 'ColorwaySelector')]//button"),
                    (By.XPATH, "//div[contains(@class, 'ColorwayStyles')]//div[contains(@class, 'ColorwayStyles-field')]")
                ]
                
                colorway_buttons = []
                for selector_type, selector in colorway_selectors:
                    try:
                        colorway_buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((selector_type, selector))
                        )
                        if colorway_buttons:
                            print(f"✅ Found {len(colorway_buttons)} colorway buttons using selector: {selector}")
                            break
                    except Exception:
                        continue
                
                if not colorway_buttons:
                    print(f"⚠️ No colorways found for {product_title}. Extracting default style only.")
                    # Create a single entry for the default colorway
                    try:
                        # Try to get the product ID from the URL
                        url_product_id = re.search(r"/([A-Z0-9]+)\.html", product_url)
                        default_product_id = url_product_id.group(1) if url_product_id else "DEFAULT"
                        
                        # Try to find supplier SKU in the page
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        sku_match = re.search(r"Supplier[-\s]sku #:?\s*(\S+)", page_text, re.IGNORECASE)
                        supplier_sku = sku_match.group(1) if sku_match else None
                        
                        if supplier_sku:
                            footlocker_deals.append({
                                "store": "Foot Locker",
                                "product_title": product_title,
                                "product_url": product_url,
                                "product_number": default_product_id,
                                "supplier_sku": supplier_sku,
                                "colorway_index": 1
                            })
                            print(f"✅ Stored default SKU: {supplier_sku} with Product # {default_product_id}")
                    except Exception as e:
                        print(f"⚠️ Error processing default product: {e}")
                    
                    continue  # Skip to next product
                
                print(f"🎨 Found {len(colorway_buttons)} colorways for {product_title}.")
                
                # Track processed colorways to avoid duplicates
                processed_colorways = set()
                
                # Process each colorway by revisiting the product page for each one
                # This helps ensure we get fresh data for each colorway
                for color_index, color_button in enumerate(colorway_buttons):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {product_title}...")
                        
                        # CRITICAL FIX: Instead of trying to click colorways on the same page,
                        # we'll get the unique URL for each colorway and visit it directly
                        
                        # First, try to get colorway product number from image
                        try:
                            colorway_img = color_button.find_element(By.TAG_NAME, "img")
                            img_src = colorway_img.get_attribute("src")
                            product_number_patterns = [
                                r"/([A-Z0-9]{6,10})\?",
                                r"_([A-Z0-9]{6,10})_",
                                r"color=([A-Z0-9]{6,10})"
                            ]
                            
                            colorway_product_number = None
                            for pattern in product_number_patterns:
                                match = re.search(pattern, img_src)
                                if match:
                                    colorway_product_number = match.group(1)
                                    break
                        except Exception as e:
                            print(f"⚠️ Error extracting colorway product number: {e}")
                            colorway_product_number = None
                        
                        if not colorway_product_number:
                            # Fallback: Try to get product ID from the colorway element
                            try:
                                element_id = color_button.get_attribute("id") or ""
                                id_match = re.search(r"([A-Z0-9]{6,10})", element_id)
                                if id_match:
                                    colorway_product_number = id_match.group(1)
                                else:
                                    # Last resort: Use a random ID
                                    colorway_product_number = f"COLOR-{color_index+1}"
                            except Exception:
                                colorway_product_number = f"COLOR-{color_index+1}"
                        
                        print(f"🔄 Identified colorway Product #: {colorway_product_number}")
                        
                        # If we've already processed this colorway, skip it
                        if colorway_product_number in processed_colorways:
                            print(f"⚠️ Already processed colorway {colorway_product_number}. Skipping.")
                            continue
                            
                        processed_colorways.add(colorway_product_number)
                        
                        # Construct direct URL for this specific colorway
                        # The URL pattern is usually domain.com/product/name/PRODUCT_NUMBER.html
                        base_url_parts = product_url.split('/')
                        if len(base_url_parts) >= 4:
                            # Replace the product number in the URL
                            base_url_parts[-1] = f"{colorway_product_number}.html"
                            colorway_url = '/'.join(base_url_parts)
                            print(f"🔗 Constructed colorway URL: {colorway_url}")
                        else:
                            # If we can't construct URL, try clicking the colorway
                            print(f"⚠️ Couldn't construct URL. Will try clicking the colorway.")
                            colorway_url = None
                        
                        if colorway_url:
                            # Visit the specific colorway URL directly
                            driver.get(colorway_url)
                            time.sleep(random.uniform(7, 10))
                            
                            # Click details tab again for this colorway
                            for selector in details_selectors:
                                try:
                                    details_element = WebDriverWait(driver, 8).until(
                                        EC.element_to_be_clickable((By.XPATH, selector))
                                    )
                                    driver.execute_script("arguments[0].click();", details_element)
                                    print(f"✅ Clicked 'Details' section for colorway {colorway_product_number}")
                                    time.sleep(random.uniform(2, 4))
                                    break
                                except Exception:
                                    continue
                        else:
                            # If we couldn't construct a URL, try clicking the colorway
                            try:
                                # Try JavaScript click which is more reliable
                                driver.execute_script("arguments[0].click();", color_button)
                                print(f"✅ Clicked on colorway [{color_index+1}]")
                                # Wait for page to update
                                time.sleep(random.uniform(5, 7))
                            except Exception as e:
                                print(f"⚠️ Failed to click colorway: {e}")
                                continue
                        
                        # Try to find the Supplier SKU - search entire page text
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        
                        # Try multiple patterns to find the supplier SKU
                        sku_patterns = [
                            r"Supplier-sku #:\s*([A-Z0-9\-]+)",
                            r"Supplier[-\s]sku:?\s*([A-Z0-9\-]+)",
                            r"Style #:\s*([A-Z0-9\-]+)",
                            r"Style:?\s*([A-Z0-9\-]+)",
                            r"Item #:\s*([A-Z0-9\-]+)"
                        ]
                        
                        supplier_sku = None
                        for pattern in sku_patterns:
                            match = re.search(pattern, page_text, re.IGNORECASE)
                            if match:
                                supplier_sku = match.group(1).strip()
                                print(f"✅ Found Supplier SKU using pattern: {pattern}")
                                break
                                
                        if not supplier_sku:
                            # Last resort: If we can derive the SKU from product number
                            if len(colorway_product_number) >= 7:
                                # Format might be like Z4549101 → DZ4549-101
                                first_part = colorway_product_number[0:5]
                                second_part = colorway_product_number[5:]
                                if len(second_part) == 3:  # Common format
                                    supplier_sku = f"{colorway_product_number[0].upper()}{first_part}-{second_part}"
                                    print(f"⚠️ Constructed supplier SKU from product number: {supplier_sku}")
                            else:
                                print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}]")
                                continue
                            
                        # Make supplier SKU uppercase for consistency
                        supplier_sku = supplier_sku.upper()
                        print(f"✅ Final Supplier SKU: {supplier_sku}")
                        
                        # Take a screenshot for reference
                        screenshot_path = f"footlocker_product_{index+1}_colorway_{color_index+1}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print(f"📷 Saved screenshot to {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to save screenshot: {e}")

                        # Save the extracted product number and supplier SKU
                        footlocker_deals.append({
                            "store": "Foot Locker",
                            "product_title": product_title,
                            "product_url": colorway_url or product_url,
                            "product_number": colorway_product_number,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_index + 1
                        })
                        print(f"✅ Stored SKU: {supplier_sku} with Product # {colorway_product_number}")

                    except StaleElementReferenceException:
                        print(f"⚠️ Stale element reference for colorway [{color_index+1}]. Re-fetching page.")
                        driver.refresh()
                        time.sleep(5)
                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_index+1}]: {e}")
                        
            except Exception as e:
                print(f"⚠️ Error processing product [{index+1}]: {e}")

    except Exception as e:
        print(f"⚠️ Main process error: {e}")
    finally:
        driver.quit()

    # Print summary of results with unique SKUs highlighted
    print("\n📊 SUMMARY RESULTS:")
    all_skus = [deal['supplier_sku'] for deal in footlocker_deals]
    unique_skus = set(all_skus)
    print(f"Total products found: {len(footlocker_deals)}")
    print(f"Unique supplier SKUs found: {len(unique_skus)}")
    
    # Print details of each unique deal
    print("\n🏁 Final Foot Locker Deals:")
    for i, deal in enumerate(footlocker_deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']})")
    
    return footlocker_deals

if __name__ == "__main__":
    print("🏃 Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
