from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)


def extract_price_info(driver):
    try:
        price_final = driver.find_element(By.XPATH, "//span[contains(@class, 'ProductPrice-final')]").text.strip()
        price_original = driver.find_element(By.XPATH, "//span[contains(@class, 'ProductPrice-original')]").text.strip()
        discount = driver.find_element(By.XPATH, "//div[contains(@class, 'ProductPrice-percent')]").text.strip()
        return price_final, price_original, discount
    except:
        return None, None, None


def get_footlocker_deals():
    search_url = "https://www.footlocker.com/search?query=air%20max%201"
    driver = create_driver()
    driver.get(search_url)

    print("\nFetching Foot Locker deals...")
    print("ℹ️ No cookie consent dialog found")

    time.sleep(3)
    product_links = []
    cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/')]")
    seen = set()
    for c in cards:
        href = c.get_attribute("href")
        if href and "/product/" in href and href not in seen:
            product_links.append(href)
            seen.add(href)

    print(f"🔎 Found {len(product_links)} products on Foot Locker.")
    print("Extracted product URLs:", product_links[:10], "..." if len(product_links) > 10 else "")

    all_deals = []
    for idx, link in enumerate(product_links[:10]):
        print(f"\n🔄 Processing Foot Locker product [{idx + 1}]...")
        try:
            driver.get(link)
            time.sleep(2)

            try:
                title_el = driver.find_element(By.CLASS_NAME, "ProductName-primary")
                subtitle_el = driver.find_element(By.CLASS_NAME, "ProductName-subtitle")
                title = f"{title_el.text.strip()} {subtitle_el.text.strip()}"
            except:
                title = "N/A"

            print(f"📝 Product Title: {title}")

            try:
                details_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='pdp-tab-details']"))
                )
                details_tab.click()
                time.sleep(1)
            except:
                print("⚠️ Warning: Could not click 'Details' tab")
                continue

            try:
                product_number = driver.find_element(
                    By.XPATH, "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
                ).text.strip()
                style_match = re.search(r"Style:\s*(\w+-\w+)", driver.page_source)
                style_id = style_match.group(1) if style_match else "N/A"
            except:
                product_number = "N/A"
                style_id = "N/A"

            price_final, price_original, discount = extract_price_info(driver)

            print(f"Base Product Number: {product_number}")
            print(f"Style ID: {style_id}")
            print(f"Price Info: {price_final} {price_original} {discount}")

            all_deals.append({
                "product_title": title,
                "product_number": product_number,
                "style_id": style_id,
                "price": price_final,
                "regular_price": price_original,
                "discount": discount,
                "url": link
            })

        except Exception as e:
            print(f"❌ Failed to process product [{idx + 1}]: {e}")

    driver.quit()

    # Summary
    total = len(all_deals)
    total_on_sale = sum(1 for d in all_deals if d["regular_price"] and d["price"] and d["price"] != d["regular_price"])
    unique_styles = len(set(d["style_id"] for d in all_deals if d["style_id"] != "N/A"))

    print("\nSUMMARY RESULTS:")
    print(f"Total unique Foot Locker products: {unique_styles}")
    print(f"Total Foot Locker variants: {total}")
    print(f"Foot Locker variants on sale: {total_on_sale}")

    return all_deals
