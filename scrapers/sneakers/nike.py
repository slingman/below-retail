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
    # Nike search URL with query and view type (if needed)
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    
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
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(@id,'accept')]"))
            ).click()
            print("✅ Clicked on cookie consent button")
            time.sleep(2)
        except Exception:
            print("ℹ️ No cookie consent dialog found")
        
        # Get product cards from the search results.
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.product-card[data-testid='product-card']")
        if not product_cards:
            print("⚠️ No products found on Nike search")
            return deals
        print(f"🔎 Found {len(product_cards)} products on Nike search")
        
        product_urls = []
        for card in product_cards:
            try:
                # Extract product URL from the overlay link.
                url = card.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay[data-testid='product-card__link-overlay']").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
        
        # Process each product URL (for example, the first 3 products).
        for idx, prod_url in enumerate(product_urls[:3], start=1):
            try:
                print(f"\n🔄 Processing Nike product [{idx}]...")
                driver.get(prod_url)
                time.sleep(8)
                
                # Extract product title.
                try:
                    prod_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='product_title']").text.strip()
                    print("📝 Product Title:", prod_title)
                except Exception as e:
                    prod_title = "Unknown Nike Product"
                    print(f"⚠️ Could not extract product title: {e}")
                
                # Extract base variant price info from the product page.
                try:
                    sale_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='currentPrice-container']").text.strip()
                except Exception:
                    sale_price = ""
                try:
                    regular_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='initialPrice-container']").text.strip()
                except Exception:
                    regular_price = ""
                try:
                    discount_percent = driver.find_element(By.CSS_SELECTOR, "span[data-testid='OfferPercentage']").text.strip()
                except Exception:
                    discount_percent = ""
                print("Base Price Info:", sale_price, regular_price, discount_percent)
                
                # Derive the base style from the product URL.
                base_style = prod_url.rstrip("/").split("/")[-1]
                print("Base Style:", base_style)
                
                # Record the base variant as a deal.
                deals.append({
                    "store": "Nike",
                    "product_name": prod_title,
                    "product_url": prod_url,
                    "style_number": base_style,
                    "sale_price": sale_price,
                    "regular_price": regular_price,
                    "discount_percent": discount_percent,
                    "colorway_index": 1
                })
                
                # Look for the colorway picker container.
                try:
                    colorway_container = driver.find_element(By.ID, "colorway-picker-container")
                    colorway_links = colorway_container.find_elements(By.TAG_NAME, "a")
                    num_colorways = len(colorway_links)
                    print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
                except Exception as e:
                    print(f"⚠️ No colorway picker found; defaulting to base variant. Error: {e}")
                    num_colorways = 0
                    colorway_links = []
                
                # Process each colorway variant (if available).
                colorway_index = 1
                for link in colorway_links:
                    try:
                        variant_href = link.get_attribute("href")
                        # Construct full URL if necessary.
                        if not variant_href.startswith("http"):
                            variant_url = "https://www.nike.com" + variant_href
                        else:
                            variant_url = variant_href
                        colorway_index += 1
                        print(f"\n🔄 Processing colorway variant [{colorway_index}] - URL: {variant_url}")
                        driver.get(variant_url)
                        time.sleep(8)
                        
                        # Extract price info from the variant page.
                        try:
                            variant_sale_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='currentPrice-container']").text.strip()
                        except Exception:
                            variant_sale_price = ""
                        try:
                            variant_regular_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='initialPrice-container']").text.strip()
                        except Exception:
                            variant_regular_price = ""
                        try:
                            variant_discount = driver.find_element(By.CSS_SELECTOR, "span[data-testid='OfferPercentage']").text.strip()
                        except Exception:
                            variant_discount = ""
                        
                        # Extract the variant style from the URL.
                        variant_style = variant_url.rstrip("/").split("/")[-1]
                        print("Variant Style:", variant_style)
                        print("Variant Price Info:", variant_sale_price, variant_regular_price, variant_discount)
                        
                        deals.append({
                            "store": "Nike",
                            "product_name": prod_title,
                            "product_url": variant_url,
                            "style_number": variant_style,
                            "sale_price": variant_sale_price,
                            "regular_price": variant_regular_price,
                            "discount_percent": variant_discount,
                            "colorway_index": colorway_index
                        })
                    except Exception as e:
                        print(f"⚠️ Error processing variant colorway: {e}")
                        traceback.print_exc()
                        
            except Exception as e:
                print(f"⚠️ Error processing Nike product [{idx}]: {e}")
                traceback.print_exc()
                
    except Exception as e:
        print("⚠️ Main Nike process error:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    
    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(deals)}")
    return deals

if __name__ == "__main__":
    print("Starting Nike scraper...")
    deals = get_nike_deals()
    print("\nFinal Nike Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_name']} (Style: {deal['style_number']}, Sale Price: {deal['sale_price']}, Regular Price: {deal['regular_price']}, Discount: {deal['discount_percent']})")
