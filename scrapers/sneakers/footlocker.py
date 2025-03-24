import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from utils.common import extract_price

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def extract_product_urls(driver):
    search_url = "https://www.footlocker.com/search?query=air%20max%201"
    driver.get(search_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/product/')]")))
    product_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/product/')]")
    urls = list({link.get_attribute("href") for link in product_links if link.get_attribute("href")})
    return urls

def get_text_safe(driver, xpath):
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()
    except:
        return None

def extract_title(driver):
    try:
        return driver.find_element(By.CLASS_NAME, "ProductDetails-title").text.strip()
    except:
        return None

def extract_supplier_sku(driver):
    xpath = "//div[@id='ProductDetails-tabs-details-panel']/span[1]"
    text = get_text_safe(driver, xpath)
    return text if text and "-" in text else None

def extract_prices(driver):
    current_price = get_text_safe(driver, "//span[contains(@class,'ProductPrice-final')]")
    original_price = get_text_safe(driver, "//span[contains(@class,'ProductPrice-original')]")
    discount = get_text_safe(driver, "//div[contains(@class,'ProductPrice-percent')]")
    return extract_price(current_price), extract_price(original_price), discount

def extract_colorways(driver):
    try:
        color_buttons = driver.find_elements(By.XPATH, "//ul[contains(@class,'ProductColorways')]//button")
        return color_buttons
    except:
        return []

def process_colorway(driver, base_url, color_btn, index):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", color_btn)
        color_btn.click()
        time.sleep(2)
        product_num = get_text_safe(driver, "//div[@id='ProductDetails-tabs-details-panel']/span[2]")
        if not product_num:
            print(f"⚠️ Could not fetch product number for colorway [{index}]")
            return None
        variant_url = f"https://www.footlocker.com/product/~/"+product_num+".html"
        driver.get(variant_url)
        time.sleep(1)
    except:
        print(f"⚠️ Skipping colorway [{index}] due to error.")
        return None

    sku = extract_supplier_sku(driver)
    price, orig_price, discount = extract_prices(driver)
    return {
        "style_id": sku,
        "price": price,
        "original_price": orig_price,
        "discount": discount
    }

def parse_product_page(driver, url, index):
    print(f"\n🔄 Processing Foot Locker product [{index + 1}]...")
    driver.get(url)
    time.sleep(2)

    title = extract_title(driver)
    base_product_number = url.split("/")[-1].replace(".html", "")
    if not title:
        print(f"⚠️ Could not extract product title, using 'Product {index + 1}'")
        title = f"Product {index + 1}"

    print(f"📝 Product Title: {title}")
    print(f"Base Product Number: {base_product_number}")

    color_buttons = extract_colorways(driver)
    print(f"🎨 Found {len(color_buttons)} colorways for product [{index + 1}].")

    variants = []
    for idx, btn in enumerate(color_buttons):
        variant = process_colorway(driver, url, btn, idx + 1)
        if variant:
            variants.append(variant)

    print("Style Variants:")
    for v in variants:
        if not v["style_id"]:
            continue
        line = f" - {v['style_id']}: ${v['price']}"
        if v['original_price']:
            line += f" → ${v['original_price']}"
        if v['discount']:
            line += f" ({v['discount']})"
        print(line)

    return variants

def get_footlocker_deals():
    print("\nFetching Foot Locker deals...")
    driver = create_driver()
    deals = []

    try:
        urls = extract_product_urls(driver)
        print(f"🔎 Found {len(urls)} products on Foot Locker.")
        print("Extracted product URLs:", urls[:10], "..." if len(urls) > 10 else "")

        for idx, url in enumerate(urls[:10]):
            variants = parse_product_page(driver, url, idx)
            deals.extend(variant for variant in variants if variant.get("style_id"))
    finally:
        driver.quit()

    print(f"\nFetched {len(deals)} Foot Locker deals.\n")
    return deals
