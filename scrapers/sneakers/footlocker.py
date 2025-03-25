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
        time.sleep(0.5)
        return elem.text.strip() or elem.get_attribute("innerText").strip()
    except Exception as e:
        print(f"⚠️ Error getting text from {xpath}: {e}")
        return ""

def extract_product_number(text):
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def extract_price_info(driver):
    try:
        price_container = driver.find_element(By.XPATH, "//div[contains(@class,'ProductPrice')]")
        final = price_container.find_element(By.XPATH, ".//span[contains(@class,'final')]").text.strip()
        try:
            original = price_container.find_element(By.XPATH, ".//span[contains(@class,'original')]").text.strip()
        except:
            original = final
        try:
            discount = price_container.find_element(By.XPATH, ".//span[contains(@class,'percent')]").text.strip()
        except:
            discount = ""
        return final, original, discount
    except Exception as e:
        print(f"⚠️ Could not extract price info: {e}")
        return "N/A", "N/A", ""

def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    variant_url_format = "https://www.footlocker.com/product/~/{0}.html"

    details_panel_xpath = "//div[@id='ProductDetails-tabs-details-panel']"
    product_num_xpath = f"{details_panel_xpath}/span[1]"
    supplier_sku_xpath = f"{details_panel_xpath}/span[2]"

    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    deals = []

    try:
        driver.get(search_url)
        time.sleep(8)

        # Try closing cookie banner
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            ).click()
            time.sleep(2)
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")

        cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        if not cards:
            print("⚠️ No products found on Foot Locker.")
            return deals

        print(f"🔎 Found {len(cards)} products on Foot Locker.")

        product_urls = []
        for card in cards[:3]:  # Limit to top 3 for now
            try:
                url = card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href")
                product_urls.append(url)
            except:
                continue
        print("Extracted product URLs:", product_urls)

        for idx, url in enumerate(product_urls, 1):
            print(f"\n🔄 Processing product [{idx}]: {url}")
            try:
                driver.get(url)
                time.sleep(6)

                try:
                    title = WebDriverWait(driver, 8).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                    ).text.strip()
                except:
                    title = f"Product {idx}"
                print(f"📝 Product Title: {title}")

                try:
                    tab = driver.find_element(By.XPATH, "//button[contains(@id,'ProductDetails-tabs-details-tab')]")
                    driver.execute_script("arguments[0].click();", tab)
                    time.sleep(2)
                    print("✅ Clicked on 'Details' section to open it")
                except:
                    print("⚠️ Could not click on 'Details' tab")

                base_text = get_element_text(driver, product_num_xpath)
                base_prod = extract_product_number(base_text)
                print("Base Product Number:", base_prod)

                color_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                if not color_buttons:
                    print("⚠️ No colorway buttons found.")
                    color_buttons = [None]

                for i, _ in enumerate(color_buttons):
                    print(f"\n🔄 Processing colorway [{i+1}] for {title}...")
                    color_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                    if i >= len(color_buttons):
                        print(f"⚠️ Index {i} out of range.")
                        continue

                    btn = color_buttons[i]
                    try:
                        img = btn.find_element(By.TAG_NAME, "img")
                        src = img.get_attribute("src")
                        match = re.search(r"/([A-Z0-9]{6,10})\?", src)
                        variant_prod = match.group(1) if match else f"UNKNOWN-{i+1}"
                    except:
                        variant_prod = f"UNKNOWN-{i+1}"
                    print("Variant Product Number:", variant_prod)

                    try:
                        ActionChains(driver).move_to_element(btn).click().perform()
                        print(f"✅ Clicked on colorway [{i+1}] using ActionChains")
                    except:
                        driver.execute_script("arguments[0].click();", btn)
                        print(f"✅ Fallback click on colorway [{i+1}]")

                    time.sleep(6)

                    updated_text = get_element_text(driver, product_num_xpath)
                    updated_prod = extract_product_number(updated_text)

                    if updated_prod != base_prod:
                        variant_url = variant_url_format.format(updated_prod)
                        print("Navigating to variant URL:", variant_url)
                        driver.get(variant_url)
                        time.sleep(6)
                        try:
                            tab = driver.find_element(By.XPATH, "//button[contains(@id,'ProductDetails-tabs-details-tab')]")
                            driver.execute_script("arguments[0].click();", tab)
                            time.sleep(2)
                            print("✅ Clicked on 'Details' section on variant page to open it")
                        except:
                            print("⚠️ Could not open details on variant page")

                    supplier_sku = get_element_text(driver, supplier_sku_xpath)
                    final_price, original_price, discount = extract_price_info(driver)
                    print(f"Price Info: {final_price} → {original_price} ({discount or 'No discount'})")

                    deals.append({
                        "store": "Foot Locker",
                        "product_title": title,
                        "product_url": url,
                        "product_number": updated_prod or base_prod,
                        "supplier_sku": supplier_sku,
                        "regular_price": original_price,
                        "sale_price": final_price,
                        "discount": discount or None
                    })
            except Exception as e:
                print(f"⚠️ Error processing product [{idx}]: {e}")
                traceback.print_exc()

    except Exception as e:
        print("⚠️ Main scraping error:", e)
        traceback.print_exc()
    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total unique Foot Locker products: {len(deals)}")
    return deals

if __name__ == "__main__":
    print("Starting Foot Locker scraper...")
    deals = get_footlocker_deals()
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_title']} | SKU: {deal['supplier_sku']} | Sale: {deal['sale_price']} | Reg: {deal['regular_price']} | Discount: {deal['discount']}")
