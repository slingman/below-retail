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
        return elem.text.strip() or elem.get_attribute("innerText").strip()
    except Exception as e:
        print(f"⚠️ Error getting text from {xpath}: {e}")
        return ""

def extract_product_number(text):
    m = re.search(r"Product #:\s*(\S+)", text)
    return m.group(1) if m else text

def extract_price_info(driver):
    try:
        final_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'final')]"
        original_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'original')]"
        discount_xpath = "//div[contains(@class, 'ProductPrice')]//span[contains(@class, 'percent')]"

        final_price = get_element_text(driver, final_xpath).replace("$", "").strip()
        original_price = get_element_text(driver, original_xpath).replace("$", "").strip()
        discount_percent = get_element_text(driver, discount_xpath).replace("%", "").strip()

        final = float(final_price) if final_price else None
        original = float(original_price) if original_price else final
        discount = int(discount_percent) if discount_percent else None

        return final, original, discount
    except Exception as e:
        print(f"⚠️ Could not extract price info: {e}")
        return None, None, None

def get_footlocker_deals():
    print("Fetching Foot Locker deals...")
    search_url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    variant_url_format = "https://www.footlocker.com/product/~/{0}.html"
    deals = []

    # Setup driver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)

    try:
        driver.get(search_url)
        time.sleep(8)

        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            ).click()
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found or couldn't be closed")

        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "ProductCard"))
        )
        print(f"🔎 Found {len(product_cards)} products on Foot Locker.")
        product_urls = [card.find_element(By.CLASS_NAME, "ProductCard-link").get_attribute("href") for card in product_cards[:3]]
        print("Extracted product URLs:", product_urls)

        for idx, url in enumerate(product_urls, 1):
            print(f"\n🔄 Processing product [{idx}]: {url}")
            try:
                driver.get(url)
                time.sleep(8)

                title_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ProductName-primary"))
                )
                title = title_elem.text.strip()
                print(f"📝 Product Title: {title}")
            except Exception:
                title = f"Product {idx}"
                print("⚠️ Could not extract title")

            try:
                tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(2)
            except:
                pass

            base_prod = extract_product_number(get_element_text(driver, "//div[@id='ProductDetails-tabs-details-panel']/span[1]"))

            try:
                colorway_buttons = driver.find_elements(By.CLASS_NAME, "ColorwayStyles-field")
                print(f"🎨 Found {len(colorway_buttons)} colorways.")
            except:
                colorway_buttons = [None]
                print("⚠️ No colorway buttons found, defaulting to 1.")

            for i, btn in enumerate(colorway_buttons):
                print(f"\n🔄 Processing colorway [{i+1}] for {title}...")
                try:
                    if btn:
                        try:
                            ActionChains(driver).move_to_element(btn).click().perform()
                        except:
                            driver.execute_script("arguments[0].click();", btn)
                        time.sleep(8)

                    variant_prod = extract_product_number(get_element_text(driver, "//div[@id='ProductDetails-tabs-details-panel']/span[1]"))
                    if variant_prod != base_prod:
                        variant_url = variant_url_format.format(variant_prod)
                        print("Navigating to variant URL:", variant_url)
                        driver.get(variant_url)
                        time.sleep(8)
                        try:
                            tab = driver.find_element(By.XPATH, "//button[contains(@id, 'ProductDetails-tabs-details-tab')]")
                            driver.execute_script("arguments[0].click();", tab)
                            time.sleep(2)
                        except:
                            pass

                    supplier_sku = get_element_text(driver, "//div[@id='ProductDetails-tabs-details-panel']/span[2]")
                    final, original, discount = extract_price_info(driver)
                    if final is None:
                        print("Price Info: N/A → N/A (No discount)")
                    else:
                        print(f"Price Info: ${final} → ${original} ({f'{discount}% off' if discount else 'No discount'})")

                    deals.append({
                        "store": "Foot Locker",
                        "product_title": title,
                        "product_url": url,
                        "product_number": variant_prod,
                        "supplier_sku": supplier_sku,
                        "price": final,
                        "original_price": original,
                        "discount_percent": discount,
                    })
                except Exception as e:
                    print(f"⚠️ Error processing colorway [{i+1}]: {e}")
                    traceback.print_exc()

    except Exception as e:
        print("❌ Failed to fetch Foot Locker deals:", e)
        traceback.print_exc()
    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total unique Foot Locker products: {len(deals)}")
    return deals

if __name__ == "__main__":
    get_footlocker_deals()
