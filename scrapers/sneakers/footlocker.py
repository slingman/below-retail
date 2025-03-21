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

# Helper: Get text from an element using .text, falling back to innerText.
def get_element_text(driver, xpath):
    try:
        elem = driver.find_element(By.XPATH, xpath)
        # Scroll element into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(1)
        text = elem.text
        if not text:
            text = elem.get_attribute("innerText")
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error getting text for {xpath}: {e}")
        return ""

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    # Base variant URL format for reloading variant pages.
    variant_url_format = "https://www.footlocker.com/product/~/{}.html"

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # For headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Use a common user agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    deals = []

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
        
        # Extract product cards from the search results
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return deals

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # Collect product URLs for the first 3 products
        product_urls = []
        for card in product_cards[:3]:
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")

        print("Extracted product URLs:", product_urls)

        # For each product URL, process its colorways
        for idx, prod_url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]...")
                driver.get(prod_url)
                time.sleep(8)
                
                # Get product title for logging
                try:
                    prod_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text.strip()
                    print(f"📝 Product Title: {prod_title}")
                except Exception:
                    prod_title = f"Product {idx}"
                    print(f"⚠️ Could not extract product title, using '{prod_title}'")
                
                # Open details section if not already open
                details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
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
                
                # Extract base product number from the details panel (first span)
                base_prod_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
                base_product_number = get_element_text(driver, base_prod_xpath)
                print(f"Base Product Number: {base_product_number}")
                
                # Get colorway buttons using multiple selectors
                colorway_selectors = [
                    (By.CLASS_NAME, "ColorwayStyles-field"),
                    (By.XPATH, "//div[contains(@class, 'ColorwaySelector')]//div[contains(@class, 'ColorwayStyles-field')]"),
                    (By.XPATH, "//div[contains(@class, 'ColorwaySelector')]//img[@alt]")
                ]
                colorway_buttons = []
                for sel_type, sel in colorway_selectors:
                    try:
                        colorway_buttons = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((sel_type, sel))
                        )
                        if colorway_buttons:
                            print(f"✅ Found colorway buttons using selector: {sel}")
                            break
                    except Exception:
                        continue
                if not colorway_buttons:
                    print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                    colorway_buttons = [None]
                else:
                    print(f"🎨 Found {len(colorway_buttons)} colorways for product [{idx}].")
                
                # Process each colorway
                for color_idx, color_button in enumerate(colorway_buttons, start=1):
                    try:
                        print(f"\n🔄 Processing colorway [{color_idx}] for {prod_title}...")
                        if color_button is not None:
                            try:
                                c_img = color_button.find_element(By.TAG_NAME, "img")
                                c_src = c_img.get_attribute("src")
                                pn_patterns = [r"/([A-Z0-9]{6,10})\?", r"_([A-Z0-9]{6,10})_", r"-([A-Z0-9]{6,10})-"]
                                variant_product_number = None
                                for pattern in pn_patterns:
                                    m = re.search(pattern, c_src)
                                    if m:
                                        variant_product_number = m.group(1)
                                        break
                            except Exception as e:
                                print(f"⚠️ Error extracting product number from image: {e}")
                                traceback.print_exc()
                                variant_product_number = f"UNKNOWN-{color_idx}"
                            if not variant_product_number:
                                variant_product_number = f"UNKNOWN-{color_idx}"
                            print(f"Variant Product Number: {variant_product_number}")
                            
                            # Click the colorway thumbnail using ActionChains
                            try:
                                actions = ActionChains(driver)
                                actions.move_to_element(color_button).click().perform()
                                print(f"✅ Clicked on colorway [{color_idx}] using ActionChains")
                            except Exception as e:
                                print(f"⚠️ ActionChains click failed: {e}")
                                driver.execute_script("arguments[0].click();", color_button)
                                print(f"✅ Clicked on colorway [{color_idx}] using JavaScript fallback")
                            
                            # After clicking, wait a bit (e.g. 5 seconds) for the DOM to update
                            time.sleep(5)
                            
                            # Read updated product number from details panel
                            updated_prod_number = get_element_text(driver, base_prod_xpath)
                            print(f"Updated Product Number in details: {updated_prod_number}")
                            
                            # If the updated product number is different from the base,
                            # construct the variant URL to force a full reload.
                            if updated_prod_number and updated_prod_number != base_product_number:
                                variant_url = "https://www.footlocker.com/product/~/" + updated_prod_number + ".html"
                                print(f"Navigating to variant URL: {variant_url}")
                                driver.get(variant_url)
                                time.sleep(8)  # Wait for variant page to load
                            else:
                                print("Base product remains; using current page for variant")
                            
                        else:
                            variant_product_number = "DEFAULT"
                            print("ℹ️ Processing default colorway only")
                        
                        # Now extract supplier SKU from the second span of the details panel
                        supplier_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"
                        supplier_sku = get_element_text(driver, supplier_xpath)
                        print(f"Extracted Supplier SKU from span: {supplier_sku}")
                        
                        if not supplier_sku:
                            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_idx}]")
                            continue
                        
                        # Save screenshot for debugging
                        screenshot_path = f"footlocker_product_{idx}_colorway_{color_idx}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print(f"📷 Saved screenshot to {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to save screenshot: {e}")
                        
                        deals.append({
                            "store": "Foot Locker",
                            "product_title": prod_title,
                            "product_url": product_url,
                            "product_number": variant_product_number,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_idx
                        })
                        print(f"✅ Stored SKU: {supplier_sku} with Product # {variant_product_number}")
                    
                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_idx}]: {e}")
                        traceback.print_exc()
                        
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error processing product [{idx}]: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print(f"⚠️ Main process error: {e}")
        traceback.print_exc()
    finally:
        driver.quit()
    
    print("\n📊 SUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}")
    
    return deals

if __name__ == "__main__":
    print("🏃 Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\n🏁 Final Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']})")
