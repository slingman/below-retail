# scrapers/sneakers/footlocker.py

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.common import extract_price


def create_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(driver=ChromeDriverManager().install(), options=options)


def get_footlocker_deals():
    driver = create_driver()
    deals = []
    try:
        print("\nFetching Foot Locker deals...")
        search_url = "https://www.footlocker.com/search?query=air%20max%201"
        driver.get(search_url)
        time.sleep(5)

        product_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/')]")
        urls = list({link.get_attribute("href").split("?")[0] for link in product_links})
        print(f"🔎 Found {len(urls)} products on Foot Locker.")
        print("Extracted product URLs:", urls[:10], "..." if len(urls) > 10 else "")

        for i, url in enumerate(urls[:10]):
            print(f"\n🔄 Processing Foot Locker product [{i + 1}]...")
            driver.get(url)
            time.sleep(2)

            try:
                title = driver.find_element(By.CLASS_NAME, "ProductName-primary").text
                subtitle = driver.find_element(By.CLASS_NAME, "ProductName-subtitle").text
                full_title = f"{title} {subtitle}".strip()
            except:
                full_title = "N/A"

            print(f"📝 Product Title: {full_title}")

            try:
                details_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Details')]"))
                )
                details_tab.click()
                time.sleep(1)
            except:
                print("⚠️ Warning: Could not click 'Details' tab")
                continue

            try:
                base_product_number = driver.current_url.split("/")[-1].replace(".html", "")
                print(f"Base Product Number: {base_product_number}")
            except:
                base_product_number = "N/A"

            try:
                colorway_buttons = driver.find_elements(By.XPATH, "//ul[contains(@class, 'ProductColorways')]//a")
                print(f"🎨 Found {len(colorway_buttons)} colorways.")
            except:
                print("⚠️ Warning: Could not find colorways.")
                continue

            for idx, btn in enumerate(colorway_buttons):
                try:
                    btn_href = btn.get_attribute("href")
                    variant_url = btn_href if "/product/" in btn_href else f"https://www.footlocker.com/product/~/{btn_href.split('/')[-1]}"
                    driver.get(variant_url)
                    time.sleep(2)

                    supplier_sku = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]").text.strip()

                    try:
                        current = extract_price(driver.find_element(By.XPATH, "//span[contains(@class, 'ProductPrice-final')]").text)
                        original = extract_price(driver.find_element(By.XPATH, "//span[contains(@class, 'ProductPrice-original')]").text)
                        discount = round((1 - (current / original)) * 100) if current < original else None
                    except:
                        current, original, discount = None, None, None

                    print(f" - {supplier_sku}: ${current} → ${original} ({f'{discount}% off' if discount else 'None'})")

                    deals.append({
                        "title": full_title,
                        "product_number": base_product_number,
                        "style_id": supplier_sku,
                        "price": current,
                        "retail_price": original,
                        "discount_percent": discount,
                        "url": variant_url,
                        "source": "Foot Locker"
                    })
                except Exception as e:
                    print(f"⚠️ Error processing colorway [{idx + 1}]: {e}")
                    continue

    finally:
        driver.quit()

    # Summary
    total_products = len(set(d['style_id'].split("-")[0] for d in deals if d['style_id']))
    total_variants = len(deals)
    sale_variants = sum(1 for d in deals if d['discount_percent'])

    print("\nSUMMARY RESULTS:")
    print(f"Total unique Foot Locker products: {total_products}")
    print(f"Total Foot Locker variants: {total_variants}")
    print(f"Foot Locker variants on sale: {sale_variants}\n")

    return deals
