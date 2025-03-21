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
        return text.strip()
    except Exception as e:
        print(f"⚠️ Error getting details text: {e}")
        return ""

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    supplier_span_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # For headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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
        
        # Fetch product cards from the search results
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return deals

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # Extract product URLs (first 3)
        product_urls = []
        for card in product_cards[:3]:
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)

        # Process each product URL separately
        for idx, prod_url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]...")
                driver.get(prod_url)
                time.sleep(8)

                # Get product title
                try:
                    prod_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text.strip()
                    print(f"📝 Product Title: {prod_title}")
                except Exception:
                    prod_title = f"Product {idx}"
                    print(f"⚠️ Could not extract product title, using '{prod_title}'")

                # Open details section if not open
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

                # Get colorway buttons (we'll re-find them by index on each loop)
                # Use one of the selectors – for simplicity, we'll use the class name
                base_selector = (By.CLASS_NAME, "ColorwayStyles-field")
                try:
                    base_colorways = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(base_selector)
                    )
                    num_colorways = len(base_colorways)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except Exception:
                    print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                    num_colorways = 1

                # Process each colorway by index (re-find element each time)
                for color_index in range(num_colorways):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {prod_title}...")
                        # Re-find colorway buttons
                        colorway_buttons = driver.find_elements(*base_selector)
                        if not colorway_buttons or color_index >= len(colorway_buttons):
                            print(f"⚠️ Could not re-find colorway button for index {color_index+1}. Skipping.")
                            continue
                        color_button = colorway_buttons[color_index]
                        
                        # Extract product number from colorway image
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
                            variant_product_number = f"UNKNOWN-{color_index+1}"
                        if not variant_product_number:
                            variant_product_number = f"UNKNOWN-{color_index+1}"
                        print(f"Variant Product Number: {variant_product_number}")
                        
                        # Click the colorway using ActionChains (re-find element each time)
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(color_button).click().perform()
                            print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
                        except Exception as e:
                            print(f"⚠️ ActionChains click failed: {e}")
                            driver.execute_script("arguments[0].click();", color_button)
                            print(f"✅ Clicked on colorway [{color_index+1}] using JavaScript fallback")
                        
                        # Dispatch a resize event to force reflow
                        driver.execute_script("window.dispatchEvent(new Event('resize'));")
                        # Wait for 15 seconds to allow the page to update fully
                        time.sleep(15)
                        
                        # Read updated supplier SKU from the second span in the details panel
                        supplier_sku = ""
                        try:
                            supplier_sku_text = driver.find_element(By.XPATH, supplier_span_xpath).text
                            supplier_sku = supplier_sku_text.split(":", 1)[-1].strip()
                            print(f"✅ Extracted Supplier SKU from span: {supplier_sku}")
                        except Exception as e:
                            print(f"⚠️ Error extracting supplier SKU from span: {e}")
                            supplier_sku = ""
                        
                        if not supplier_sku:
                            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}].")
                            continue
                        
                        screenshot_path = f"footlocker_product_{idx}_colorway_{color_index+1}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print(f"📷 Saved screenshot to {screenshot_path}")
                        except Exception as e:
                            print(f"⚠️ Failed to save screenshot: {e}")
                        
                        deals.append({
                            "store": "Foot Locker",
                            "product_title": prod_title,
                            "product_url": prod_url,
                            "product_number": variant_product_number,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_index+1
                        })
                        print(f"✅ Stored SKU: {supplier_sku} with Product # {variant_product_number}")
                    
                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_index+1}]: {e}")
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
