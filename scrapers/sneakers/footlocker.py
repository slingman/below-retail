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

def get_element_text(driver, xpath):
    try:
        elem = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(1)
        text = elem.text.strip()
        if not text:
            text = elem.get_attribute("innerText").strip()
        return text
    except Exception as e:
        print(f"⚠️ Error getting text from {xpath}: {e}")
        return ""

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    # XPaths for details panel elements:
    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    supplier_sku_xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[2]"

    # Variant URL format:
    variant_url_format = "https://www.footlocker.com/product/~/{variant}.html"

    # Set up WebDriver
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
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

        # Cookie consent
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'accept') or contains(@id, 'accept')]"))
            ).click()
            print("✅ Clicked on cookie accept button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")
        
        # Get product cards on the search page
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not product_cards:
            print("⚠️ No products found on Foot Locker.")
            return deals

        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")

        # Extract URLs for first 3 products
        product_urls = []
        for card in product_cards[:3]:
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)

        # Process each product URL
        for idx, url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]...")
                driver.get(url)
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

                # Open details section (if not already open)
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

                # Get base product number from details panel
                base_prod = get_element_text(driver, product_num_xpath)
                print("Base Product Number:", base_prod)

                # Get colorway buttons (using class selector)
                try:
                    colorway_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "ColorwayStyles-field"))
                    )
                    num_colorways = len(colorway_buttons)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except Exception:
                    print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                    num_colorways = 1
                    colorway_buttons = [None]

                # Process each colorway by index (re-find each time)
                for color_index in range(num_colorways):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {prod_title}...")
                        # Re-find the colorway button by index
                        colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                        if color_index >= len(colorway_buttons):
                            print(f"⚠️ No colorway button at index {color_index+1}. Skipping.")
                            continue
                        color_button = colorway_buttons[color_index]
                        
                        # Extract variant product number from colorway image
                        try:
                            c_img = color_button.find_element(By.TAG_NAME, "img")
                            c_src = c_img.get_attribute("src")
                            pn_patterns = [r"/([A-Z0-9]{6,10})\?", r"_([A-Z0-9]{6,10})_", r"-([A-Z0-9]{6,10})-"]
                            variant_prod = None
                            for pat in pn_patterns:
                                m = re.search(pat, c_src)
                                if m:
                                    variant_prod = m.group(1)
                                    break
                        except Exception as e:
                            print(f"⚠️ Error extracting variant product number: {e}")
                            traceback.print_exc()
                            variant_prod = f"UNKNOWN-{color_index+1}"
                        if not variant_prod:
                            variant_prod = f"UNKNOWN-{color_index+1}"
                        print("Variant Product Number:", variant_prod)
                        
                        # Click the colorway thumbnail using ActionChains
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(color_button).click().perform()
                            print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
                        except Exception as e:
                            print(f"⚠️ ActionChains click failed: {e}")
                            driver.execute_script("arguments[0].click();", color_button)
                            print(f"✅ Clicked on colorway [{color_index+1}] using JavaScript fallback")
                        
                        # Wait a fixed time to let the page update (e.g., 10 seconds)
                        time.sleep(10)
                        
                        # Re-read the updated product number from details panel
                        updated_prod = get_element_text(driver, product_num_xpath)
                        print("Updated Product Number:", updated_prod)
                        
                        # If variant product number differs from base, assume a variant update and navigate to variant URL
                        if updated_prod and updated_prod != base_prod:
                            variant_url = variant_url_format.format(updated_prod)
                            print("Navigating to variant URL:", variant_url)
                            driver.get(variant_url)
                            time.sleep(8)
                        
                        # Now extract the supplier SKU from the supplier span
                        supplier_sku = get_element_text(driver, supplier_span_xpath)
                        print("Extracted Supplier SKU from span:", supplier_sku)
                        
                        if not supplier_sku:
                            print(f"⚠️ Could not extract Supplier SKU for colorway [{color_index+1}].")
                            continue
                        
                        screenshot_path = f"footlocker_product_{idx}_colorway_{color_index+1}.png"
                        try:
                            driver.save_screenshot(screenshot_path)
                            print("📷 Saved screenshot to", screenshot_path)
                        except Exception as e:
                            print("⚠️ Failed to save screenshot:", e)
                        
                        deals.append({
                            "store": "Foot Locker",
                            "product_title": prod_title,
                            "product_url": prod_url,
                            "product_number": updated_prod if updated_prod else base_prod,
                            "supplier_sku": supplier_sku,
                            "colorway_index": color_index+1
                        })
                        print("✅ Stored SKU:", supplier_sku, "with Product #", updated_prod if updated_prod else base_prod)
                    
                    except Exception as e:
                        print(f"⚠️ Error processing colorway [{color_index+1}]:", e)
                        traceback.print_exc()
                        
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error processing product [{idx}]:", e)
                traceback.print_exc()
                
    except Exception as e:
        print("⚠️ Main process error:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    
    print("\nSUMMARY RESULTS:")
    print(f"Total products with unique SKUs found: {len(deals)}")
    
    return deals

if __name__ == "__main__":
    print("Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    print("\nFinal Foot Locker Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} (SKU: {deal['supplier_sku']}, Product #: {deal['product_number']})")
