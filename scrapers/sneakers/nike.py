import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def get_style_id(driver):
    try:
        style_text = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-description-style-color"]').text
        return style_text.replace("Style:", "").strip()
    except:
        return "N/A"


def scrape_colorway_variants(driver, wait, base_url):
    variants = []

    try:
        wait.until(EC.presence_of_element_located((By.ID, "colorway-picker-container")))
        colorway_container = driver.find_element(By.ID, "colorway-picker-container")
        colorway_links = colorway_container.find_elements(By.TAG_NAME, "a")

        current_style_id = get_style_id(driver)

        for link in colorway_links:
            try:
                href = link.get_attribute("href")
                style_id_match = re.search(r'/([A-Z0-9]{6}-\d{3})$', href)
                if not style_id_match:
                    continue

                style_id = style_id_match.group(1)

                if style_id == current_style_id:
                    continue

                driver.execute_script("window.open(arguments[0]);", href)
                driver.switch_to.window(driver.window_handles[-1])

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product_title"]'))
                )

                variant_title = driver.find_element(By.CSS_SELECTOR, '[data-testid="product_title"]').text.strip()
                variant_style_id = get_style_id(driver)

                try:
                    sale_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text.strip()
                except:
                    sale_price = "N/A"

                try:
                    original_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="initialPrice-container"]').text.strip()
                except:
                    original_price = sale_price

                discount = "0%"
                try:
                    orig_val = float(original_price.replace("$", "").replace(",", ""))
                    sale_val = float(sale_price.replace("$", "").replace(",", ""))
                    if sale_val < orig_val:
                        discount = f"{round((orig_val - sale_val) / orig_val * 100)}%"
                except:
                    pass

                variants.append({
                    "title": variant_title,
                    "style_id": variant_style_id,
                    "original_price": original_price,
                    "sale_price": sale_price,
                    "discount": discount,
                    "url": href
                })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"❌ Variant error: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

    except TimeoutException:
        print("⚠️ No colorway picker found.")

    return variants


def parse_nike_product_page(driver, wait, url):
    driver.get(url)

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product_title"]')))
    except TimeoutException:
        print("❌ Product page did not load.")
        return

    title = driver.find_element(By.CSS_SELECTOR, '[data-testid="product_title"]').text.strip()
    style_id = get_style_id(driver)

    try:
        sale_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text.strip()
    except:
        sale_price = "N/A"

    try:
        original_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="initialPrice-container"]').text.strip()
    except:
        original_price = sale_price

    discount = "0%"
    try:
        orig_val = float(original_price.replace("$", "").replace(",", ""))
        sale_val = float(sale_price.replace("$", "").replace(",", ""))
        if sale_val < orig_val:
            discount = f"{round((orig_val - sale_val) / orig_val * 100)}%"
    except:
        pass

    print(f"\n🟩 {title}")
    print(f"Style ID: {style_id}")
    print(f"Price: {sale_price} (was {original_price}, {discount} off)")
    print(f"URL: {url}")

    variants = scrape_colorway_variants(driver, wait, url)
    for v in variants:
        print(f"  └▶ {v['style_id']} | {v['sale_price']} (was {v['original_price']}, {v['discount']} off)")

    return {
        "title": title,
        "style_id": style_id,
        "price": sale_price,
        "original_price": original_price,
        "discount": discount,
        "url": url,
        "variants": variants
    }


def scrape_nike_air_max_1():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    base_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver.get(base_url)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link')))
        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link')
        unique_urls = list({link.get_attribute("href") for link in product_links})
        print(f"🔎 Found {len(unique_urls)} products.\n")

        all_data = []
        for url in unique_urls:
            data = parse_nike_product_page(driver, wait, url)
            if data:
                all_data.append(data)

        print(f"\n✅ Total products: {len(all_data)}")
        print(f"✅ Total variants: {sum(len(p['variants']) for p in all_data)}")
        print(f"✅ Total on sale: {sum(1 for p in all_data if p['discount'] != '0%') + sum(1 for p in all_data for v in p['variants'] if v['discount'] != '0%')}")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_nike_air_max_1()
