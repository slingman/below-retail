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

def init_driver():
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
    return driver

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    details_tab_xpath = "//button[contains(@id, 'pdp-tab-details')]"
    style_number_xpath = "//div[contains(@class, 'product-details-panel')]/span[1]"
    sale_price_css = "span[data-testid='currentPrice-container']"
    regular_price_css = "span[data-testid='initialPrice-container']"
    discount_percent_css = "span[data-testid='OfferPercentage']"
    colorway_buttons_class = "ColorwaySelector"
    
    driver = init_driver()
    deals = []
    try:
        driver.get(search_url)
        time.sleep(5)
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept') or contains(@id,'accept')]"))
            ).click()
            print("✅ Clicked on cookie consent")
        except Exception:
            print("ℹ️ No cookie consent dialog found")
        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.product-card[data-testid='product-card']")
        if not product_cards:
            print("⚠️ No products found on Nike search")
            return deals
        print(f"🔎 Found {len(product_cards)} products on Nike search")
        product_urls = []
        for card in product_cards:
            try:
                url = card.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay[data-testid='product-card__link-overlay']").get_attribute("href")
                product_urls.append(url)
            except Exception as e:
                print(f"⚠️ Error extracting product URL: {e}")
        print("Extracted product URLs:", product_urls)
    except Exception as e:
        print("⚠️ Error processing search page:", e)
    finally:
        driver.quit()
    
    # Process a limited number of products (first 3) to reduce runtime
    for idx, prod_url in enumerate(product_urls[:3], start=1):
        try:
            print(f"\n🔄 Processing Nike product [{idx}]...")
            driver = init_driver()
            driver.get(prod_url)
            time.sleep(5)
            try:
                prod_title = driver.find_element(By.CSS_SELECTOR, "h1[data-testid='product_title']").text.strip()
                print("📝 Product Title:", prod_title)
            except Exception as e:
                prod_title = f"Product {idx}"
                print(f"⚠️ Could not extract product title, using '{prod_title}':", e)
            try:
                details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                driver.execute_script("arguments[0].click();", details_tab)
                print("✅ Clicked on Details tab")
                time.sleep(2)
            except Exception:
                print("ℹ️ Details tab not found or already open")
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
            print("Base Price Info:", sale_price, regular_price, discount_percent)
            base_style = prod_url.rstrip("/").split("/")[-1]
            print("Base Style:", base_style)
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
            try:
                colorway_buttons = driver.find_elements(By.CLASS_NAME, colorway_buttons_class)
                num_colorways = len(colorway_buttons)
                print(f"🎨 Found {num_colorways} colorways for product [{idx}].")
            except Exception:
                print(f"⚠️ No colorways found for product [{idx}].")
                num_colorways = 0
            driver.quit()
            # Extract variant URLs from the colorway picker container
            driver = init_driver()
            driver.get(prod_url)
            time.sleep(5)
            try:
                container = driver.find_element(By.ID, "colorway-picker-container")
                links = container.find_elements(By.TAG_NAME, "a")
                colorway_hrefs = []
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        if not href.startswith("http"):
                            href = "https://www.nike.com" + href
                        colorway_hrefs.append(href)
                print(f"Debug: Found {len(colorway_hrefs)} colorway URLs.")
            except Exception as e:
                print(f"⚠️ No colorway picker found; defaulting to base product. Error: {e}")
                colorway_hrefs = []
            driver.quit()
            # Process each variant URL from the list (skip index 0 as that is base)
            for color_index in range(1, len(colorway_hrefs)):
                variant_url = colorway_hrefs[color_index]
                try:
                    print(f"\n🔄 Processing colorway variant [{color_index+1}] - URL: {variant_url}")
                    driver = init_driver()
                    try:
                        driver.get(variant_url)
                    except Exception as e:
                        print(f"⚠️ Error navigating to variant URL: {e}")
                        driver.quit()
                        continue
                    time.sleep(5)
                    try:
                        details_tab = driver.find_element(By.XPATH, details_tab_xpath)
                        driver.execute_script("arguments[0].click();", details_tab)
                        print("✅ Clicked on Details tab on variant page")
                        time.sleep(2)
                    except Exception:
                        print("ℹ️ Details tab not found on variant page")
                    try:
                        variant_sale_price = driver.find_element(By.CSS_SELECTOR, sale_price_css).text.strip()
                    except Exception:
                        variant_sale_price = ""
                    try:
                        variant_regular_price = driver.find_element(By.CSS_SELECTOR, regular_price_css).text.strip()
                    except Exception:
                        variant_regular_price = ""
                    try:
                        variant_discount = driver.find_element(By.CSS_SELECTOR, discount_percent_css).text.strip()
                    except Exception:
                        variant_discount = ""
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
                        "colorway_index": color_index+1
                    })
                except Exception as e:
                    print(f"⚠️ Error processing variant colorway [{color_index+1}]:", e)
                    traceback.print_exc()
                finally:
                    driver.quit()
        except Exception as e:
            print(f"⚠️ Error processing Nike product [{idx}]:", e)
            traceback.print_exc()
    except Exception as e:
        print("⚠️ Main Nike process error:", e)
        traceback.print_exc()
    return deals

if __name__ == "__main__":
    print("Starting Nike scraper...")
    deals = get_nike_deals()
    print("\nFinal Nike Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_name']} (Style: {deal['style_number']}, Sale Price: {deal['sale_price']}, Regular Price: {deal['regular_price']}, Discount: {deal['discount_percent']})")
