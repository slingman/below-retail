import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.common import extract_price


def create_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def get_footlocker_deals():
    print("\nFetching Foot Locker deals...")
    driver = create_driver()
    search_url = "https://www.footlocker.com/search?query=air%20max%201"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/product/')]")))
    except:
        print("⚠️ No product cards found")
        driver.quit()
        return []

    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/')]")
    product_urls = list({link.get_attribute("href") for link in links if "/product/" in link.get_attribute("href")})
    print(f"🔎 Found {len(product_urls)} products on Foot Locker.")
    print(f"Extracted product URLs: {product_urls[:10]}{'...' if len(product_urls) > 10 else ''}\n")

    all_deals = []
    product_count = 0
    for url in product_urls:
        product_count += 1
        print(f"🔄 Processing Foot Locker product [{product_count}]: {url}")
        try:
            driver.get(url)
            time.sleep(1)

            title_elem = driver.find_element(By.CLASS_NAME, "ProductDetails-title")
            subtitle_elem = driver.find_element(By.CLASS_NAME, "ProductDetails-subtitle")
            product_title = title_elem.text.strip() if title_elem else f"Product {product_count}"
            product_sub = subtitle_elem.text.strip() if subtitle_elem else ""
            full_title = f"{product_title} {product_sub}".strip()
            print(f"📝 Product Title: {full_title}")

            base_product_number = url.split("/")[-1].replace(".html", "")
            print(f"🔢 Base Product Number: {base_product_number}")

            try:
                details_tab = driver.find_element(By.XPATH, "//button[contains(text(),'Details')]")
                details_tab.click()
                time.sleep(1)
            except:
                print("⚠️ Warning: Could not click 'Details' tab")

            colorways = driver.find_elements(By.XPATH, "//ul[contains(@class,'ProductColorways')]/li")
            print(f"🎨 Found {len(colorways)} colorways.")

            for index, colorway in enumerate(colorways, 1):
                print(f"\n🔄 Processing colorway [{index}]...")
                try:
                    driver.execute_script("arguments[0].click();", colorway)
                    time.sleep(2)

                    # detect if URL changed (indicates navigation to variant)
                    new_url = driver.current_url
                    if base_product_number not in new_url:
                        print(f"🔁 Navigated to variant URL: {new_url}")
                        driver.get(new_url)
                        time.sleep(1)

                    sku_elem = driver.find_element(By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]")
                    supplier_sku = sku_elem.text.strip() if sku_elem else "N/A"
                    print(f"🔖 Supplier SKU: {supplier_sku}")

                    price_final = extract_text_or_none(driver, "//div[contains(@class,'ProductPrice')]//span[contains(@class,'ProductPrice-final')]")
                    price_original = extract_text_or_none(driver, "//div[contains(@class,'ProductPrice')]//span[contains(@class,'ProductPrice-original')]")
                    price_discount = extract_text_or_none(driver, "//div[contains(@class,'ProductPrice-percent')]")

                    print(f"💲 Price Info: {price_final} {price_original} {price_discount}")

                    all_deals.append({
                        "title": full_title,
                        "style_id": supplier_sku,
                        "price": extract_price(price_original or price_final),
                        "sale_price": extract_price(price_final),
                        "url": new_url,
                        "source": "Foot Locker"
                    })
                except Exception as e:
                    print(f"⚠️ Skipping colorway [{index}] due to error: {e}")

        except Exception as e:
            print(f"❌ Skipping product [{product_count}] due to error: {e}")
            continue

    driver.quit()

    print(f"\nSUMMARY RESULTS:")
    print(f"Total Foot Locker deals found: {len(all_deals)}")
    return all_deals


def extract_text_or_none(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        print(f"⚠️ Warning: Could not get text from {xpath}.")
        return None
