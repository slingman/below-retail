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

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air+max+1"
    # Selectors for Nike details.
    details_tab_xpath = "//button[contains(@id, 'pdp-tab-details')]"  # Assumed selector for a Details tab
    details_panel_xpath = "//div[contains(@class, 'product-details-panel')]"  # Container for details
    style_number_xpath = "//div[contains(@class, 'product-details-panel')]/span[1]"  # Base style number element
    sale_price_css = "span[data-testid='currentPrice-container']"
    regular_price_css = "span[data-testid='initialPrice-container']"
    discount_percent_css = "span[data-testid='OfferPercentage']"
    colorway_buttons_class = "ColorwaySelector"  # Assumed class for colorway buttons

    # Set up Selenium WebDriver.
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/90.0.4430.212 Safari/537.36")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    
    deals = []
    
    try:
        driver.get(search_url)
        time.sleep(8)
        
        # Handle cookie consent if present.
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(),'Accept') or contains(@id,'accept')]")
                )
            ).click()
            print("✅ Clicked on cookie consent button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found")
        
        # Get product cards from search results.
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
        )
        if not product_cards:
            print("⚠️ No products found on Nike.")
            return deals
        print(f"🔎 Found {len(product_cards)} products on Nike.")
        
        product_urls = []
        for card in product_cards[:3]:
            try:
                product_url = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card__link-overlay']").get_attribute("href")
                product_urls.append(product_url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
        
        # Process each product URL.
        for idx, prod_url in enumerate(product_urls, start=1):
            try:
                print(f"\n🔄 Processing product [{idx}]...")
                driver.get(prod_url)
                time.sleep(8)
                
                # Extract product title.
                try:
                    prod_title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1#pdp_product_title"))
                    ).text.strip()
                    print(f"📝 Product Title: {prod_title}")
                except Exception:
                    try:
                        prod_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='product_title']").text.strip()
                    except Exception as e:
                        prod_title = f"Product {idx}"
                        print(f"⚠️ Could not extract product title, using '{prod_title}'")
                
                # Attempt to click the Details tab, if available.
                try:
                    details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                    driver.execute_script("arguments[0].click();", details_tab)
                    print("✅ Clicked on Details tab")
                    time.sleep(3)
                except Exception:
                    print("ℹ️ Details tab not found or already open")
                
                # Extract the base style number.
                try:
                    base_text = driver.find_element(By.XPATH, style_number_xpath).text.strip()
                except Exception as e:
                    base_text = ""
                    print(f"⚠️ Could not extract base style number: {e}")
                base_style = base_text
                print("Base Style:", base_style)
                
                # Find colorway buttons.
                try:
                    colorway_buttons = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, colorway_buttons_class))
                    )
                    num_colorways = len(colorway_buttons)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except Exception:
                    print(f"⚠️ No colorways found for product [{idx}]. Using default style.")
                    num_colorways = 1
                    colorway_buttons = [None]
                
                # Process each colorway.
                for color_index in range(num_colorways):
                    try:
                        print(f"\n🔄 Processing colorway [{color_index+1}] for {prod_title}...")
                        colorway_buttons = driver.find_elements(By.CLASS_NAME, colorway_buttons_class)
                        if color_index >= len(colorway_buttons):
                            print(f"⚠️ No colorway button at index {color_index+1}. Skipping.")
                            continue
                        color_button = colorway_buttons[color_index]
                        
                        # Extract variant style from the colorway image.
                        try:
                            c_img = color_button.find_element(By.TAG_NAME, "img")
                            c_src = c_img.get_attribute("src")
                            pn_patterns = [r"/([A-Z0-9]{6,10})\?", r"_([A-Z0-9]{6,10})_", r"-([A-Z0-9]{6,10})-"]
                            variant_style = None
                            for pat in pn_patterns:
                                m = re.search(pat, c_src)
                                if m:
                                    variant_style = m.group(1)
                                    break
                        except Exception as e:
                            print(f"⚠️ Error extracting variant style: {e}")
                            traceback.print_exc()
                            variant_style = f"UNKNOWN-{color_index+1}"
                        if not variant_style:
                            variant_style = f"UNKNOWN-{color_index+1}"
                        print("Variant Style:", variant_style)
                        
                        # Click the colorway thumbnail.
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(color_button).click().perform()
                            print(f"✅ Clicked on colorway [{color_index+1}] using ActionChains")
                        except Exception as e:
                            print(f"⚠️ ActionChains click failed: {e}")
                            driver.execute_script("arguments[0].click();", color_button)
                            print(f"✅ Clicked on colorway [{color_index+1}] using JavaScript fallback")
                        
                        driver.execute_script("window.dispatchEvent(new Event('resize'));")
                        time.sleep(15)
                        
                        # Re-read updated style number.
                        try:
                            updated_text = driver.find_element(By.XPATH, style_number_xpath).text.strip()
                        except Exception as e:
                            updated_text = ""
                            print(f"⚠️ Could not re-read updated style number: {e}")
                        updated_style = updated_text if updated_text else base_style
                        print("Updated Style:", updated_style)
                        
                        # If updated style differs, assume a variant URL change.
                        if updated_style and updated_style != base_style:
                            variant_url = prod_url.replace(base_style, updated_style)
                            print("Navigating to variant URL:", variant_url)
                            driver.get(variant_url)
                            time.sleep(8)
                            try:
                                details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                                driver.execute_script("arguments[0].click();", details_tab)
                                print("✅ Clicked on Details tab on variant page")
                                time.sleep(3)
                            except Exception:
                                print("ℹ️ Details tab not found or already open on variant page")
                        else:
                            print("Base style remains; using current page for variant")
                        
                        # Extract price information.
                        try:
                            sale_price = driver.find_element(By.CSS_SELECTOR, sale_price_css).text.strip()
                        except Exception:
                            sale_price = ""
                        try:
                            regular_price = driver.find_element(By.CSS_SELECTOR, regular_price_css).text.strip()
                        except Exception:
                            regular_price = ""
                        try:
                            discount_percent = driver.find_element(By.CSS_SELECTOR, discount_percent_css).text.strip()
                        except Exception:
                            discount_percent = ""
                        print("Extracted Sale Price:", sale_price)
                        print("Extracted Regular Price:", regular_price)
                        print("Extracted Discount Percent:", discount_percent)
                        
                        deals.append({
                            "store": "Nike",
                            "product_name": prod_title,
                            "product_url": prod_url,
                            "style_number": updated_style if updated_style else base_style,
                            "sale_price": sale_price,
                            "regular_price": regular_price,
                            "discount_percent": discount_percent,
                            "colorway_index": color_index + 1
                        })
                        print("✅ Stored Style:", updated_style if updated_style else base_style)
                    
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
    print(f"Total Nike products processed: {len(deals)}")
    
    return deals

if __name__ == "__main__":
    print("Starting Nike scraper...")
    deals = get_nike_deals()
    print("\nFinal Nike Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_name']} (Style: {deal['style_number']}, Sale Price: {deal['sale_price']}, Regular Price: {deal['regular_price']}, Discount: {deal['discount_percent']})")
