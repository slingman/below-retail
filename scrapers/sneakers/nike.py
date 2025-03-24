import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_text_safe(driver, by, value):
    try:
        return driver.find_element(by, value).text.strip()
    except:
        return None

def extract_prices(driver):
    sale = get_text_safe(driver, By.CSS_SELECTOR, '[data-testid="currentPrice-container"]')
    regular = get_text_safe(driver, By.CSS_SELECTOR, '[data-testid="initialPrice-container"]')
    return sale or regular, regular if sale else None

def extract_style_id(driver):
    try:
        details = driver.find_element(By.ID, "product-description-container").text
        match = re.search(r"Style:\s+(\S+)", details)
        return match.group(1) if match else None
    except:
        return None

def get_variant_urls(driver):
    variant_links = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="colorway-link-"]')
    urls = []
    for link in variant_links:
        href = link.get_attribute("href")
        if href and href.startswith("/t/"):
            urls.append("https://www.nike.com" + href)
    return urls

def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(2)
    product_title = get_text_safe(driver, By.CSS_SELECTOR, '[data-testid="product_title"]')
    style_id = extract_style_id(driver)
    sale_price, regular_price = extract_prices(driver)

    return {
        "url": url,
        "title": product_title,
        "style_id": style_id,
        "sale_price": sale_price,
        "regular_price": regular_price
    }

def scrape_nike():
    driver = create_driver()
    driver.get(NIKE_SEARCH_URL)
    print("\nFetching Nike deals...")

    try:
        # Accept cookies
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
            ).click()
            print("✅ Accepted cookie banner")
        except:
            print("ℹ️ No cookie consent dialog found")

        # Collect product links
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay'))
        )
        product_links = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        product_urls = list({link.get_attribute("href") for link in product_links if "/t/" in link.get_attribute("href")})
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls[:10])
    except Exception as e:
        print("❌ Error collecting product URLs:", e)
        driver.quit()
        return []

    deals = []

    for idx, url in enumerate(product_urls[:10], 1):  # limit for speed
        print(f"\n🔄 Processing Nike product [{idx}]...")
        data = parse_product_page(driver, url)

        if not data["title"]:
            print("📝 Product Title: N/A")
            print("Style Variants:\n - N/A: $None")
            continue

        print(f"📝 Product Title: {data['title']}")
        print(f"Base Style: {data['style_id']}")
        print(f"Base Price Info:  {data['sale_price']} → {data['regular_price']}")

        # Get variant pages
        variants = []
        try:
            variant_urls = get_variant_urls(driver)
            print(f"Other Colorways: {len(variant_urls)} variants")
            for v_url in variant_urls:
                v_data = parse_product_page(driver, v_url)
                variants.append(v_data)
        except Exception as e:
            print("⚠️ Could not fetch variant colorways:", e)

        print("Style Variants:")
        for v in variants:
            print(f" - {v['style_id']}: ${v['sale_price']} {'→ $'+v['regular_price'] if v['regular_price'] else ''}")
        deals.append({"title": data["title"], "style_id": data["style_id"], "variants": variants})

    driver.quit()
    print(f"\nSUMMARY RESULTS:\nTotal Nike deals processed: {len(deals)}\n")
    return deals

def get_nike_deals():
    return scrape_nike()
