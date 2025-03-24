import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_text_safe(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return None

def extract_price_block(driver):
    try:
        price_block = driver.find_element(By.XPATH, "//div[@id='price-container']")
        price_html = price_block.get_attribute("innerHTML")
        sale_price = None
        reg_price = None

        sale_match = re.search(r'data-testid="currentPrice-container">([^<]+)</span>', price_html)
        if sale_match:
            sale_price = sale_match.group(1).strip()

        reg_match = re.search(r'data-testid="initialPrice-container"[^>]*>([^<]+)</span>', price_html)
        if reg_match:
            reg_price = reg_match.group(1).strip()

        if not reg_price and sale_price:
            reg_price = sale_price

        return reg_price, sale_price
    except:
        return None, None

def parse_variant(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        title = get_text_safe(driver, "//h1[@data-testid='product_title']")
        style = get_text_safe(driver, "//li[contains(@data-testid, 'product-description-style-color')]")
        if style and ":" in style:
            style = style.split(":")[-1].strip()
        reg_price, sale_price = extract_price_block(driver)
        return {
            "variant_url": url,
            "product_title": title,
            "style_id": style,
            "regular_price": reg_price,
            "sale_price": sale_price
        }
    except Exception as e:
        print(f"⚠️ Error parsing variant page {url}: {e}")
        return None

def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(2)

    print(f"🔄 Processing Nike product: {url}")

    product_title = get_text_safe(driver, "//h1[@data-testid='product_title']")
    style_id = get_text_safe(driver, "//li[contains(@data-testid, 'product-description-style-color')]")
    if style_id and ":" in style_id:
        style_id = style_id.split(":")[-1].strip()
    regular_price, sale_price = extract_price_block(driver)

    print(f"📝 Product Title: {product_title}")
    print(f"Base Style: {style_id}")
    print(f"Base Price Info:  {sale_price or regular_price} → {regular_price if sale_price else 'None'}")

    variants = []
    try:
        variant_links = driver.find_elements(By.XPATH, "//a[starts-with(@data-testid, 'colorway-link-')]")
        print(f"Other Colorways: {len(variant_links)} variants")
        for link in variant_links:
            href = link.get_attribute("href")
            if href and style_id not in href:
                variant_info = parse_variant(driver, href)
                if variant_info:
                    variants.append(variant_info)
    except Exception as e:
        print("⚠️ Error extracting variants:", e)
        traceback.print_exc()

    return {
        "product_url": url,
        "product_title": product_title,
        "style_id": style_id,
        "regular_price": regular_price,
        "sale_price": sale_price,
        "variants": variants
    }

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_driver()
    deals = []

    try:
        driver.get(search_url)
        time.sleep(2)

        try:
            consent_button = driver.find_element(By.XPATH, "//button[contains(text(),'Accept')]")
            consent_button.click()
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found")

        product_cards = driver.find_elements(By.XPATH, "//a[@data-testid='product-card__img-link-overlay']")
        product_urls = [elem.get_attribute("href") for elem in product_cards if elem.get_attribute("href")]
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        product_urls = list(dict.fromkeys(product_urls))  # remove duplicates
        print("Extracted product URLs:", product_urls[:10])

        for idx, url in enumerate(product_urls[:10], 1):
            try:
                data = parse_product_page(driver, url)
                deals.append(data)
                print("Style Variants:")
                for v in data["variants"]:
                    print(f" - {v['style_id']}: ${v['sale_price'] or v['regular_price']}")
            except Exception as e:
                print(f"⚠️ Error processing product {idx}: {e}")
                traceback.print_exc()

    finally:
        driver.quit()

    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(deals)}\n")
    return deals

if __name__ == "__main__":
    get_nike_deals()
