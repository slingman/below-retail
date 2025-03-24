import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def extract_text_safe(driver, by, value, timeout=5):
    try:
        elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return elem.text.strip()
    except:
        return "N/A"

def extract_price_data(driver):
    try:
        price_container = driver.find_element(By.ID, "price-container")
        price_text = price_container.text.strip().replace('\n', ' ')
        match = re.search(r"\$(\d+\.?\d*)", price_text)
        regular = re.search(r"List: \$(\d+\.?\d*)", price_text)
        discount = re.search(r"(\d+%) off", price_text)
        return {
            "sale_price": f"${match.group(1)}" if match else None,
            "regular_price": f"${regular.group(1)}" if regular else None,
            "discount": discount.group(1) if discount else None
        }
    except:
        return {
            "sale_price": None,
            "regular_price": None,
            "discount": None
        }

def parse_colorway_variants(driver):
    variant_data = []
    try:
        variant_links = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid^="colorway-link-"]')
        for variant in variant_links:
            href = variant.get_attribute("href")
            style_id_match = re.search(r'/([^/]+)$', href)
            style_id = style_id_match.group(1) if style_id_match else "N/A"
            alt = variant.find_element(By.TAG_NAME, "img").get_attribute("alt")
            variant_data.append({
                "style_id": style_id,
                "url": href,
                "alt_text": alt
            })
    except Exception as e:
        print("⚠️ Error extracting colorway variants:", e)
    return variant_data

def parse_product_page(driver, url):
    driver.get(url)
    time.sleep(2)
    title = extract_text_safe(driver, By.ID, "pdp_product_title")
    style_id = extract_text_safe(driver, By.XPATH, "//ul/li[contains(text(),'Style')]")
    style_id = style_id.replace("Style:", "").strip() if "Style:" in style_id else style_id
    price_info = extract_price_data(driver)
    variants = parse_colorway_variants(driver)
    return {
        "product_title": title,
        "style_id": style_id,
        **price_info,
        "variants": variants
    }

def scrape_nike():
    driver = create_driver()
    deals = []
    try:
        print("Fetching Nike deals...")
        driver.get(NIKE_SEARCH_URL)

        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
            ).click()
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found")

        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-testid='product-card__link-overlay']"))
        )
        product_urls = [card.get_attribute("href") for card in product_cards[:10]]
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls)

        for idx, url in enumerate(product_urls, 1):
            try:
                print(f"\n🔄 Processing Nike product [{idx}]...")
                product_info = parse_product_page(driver, url)
                print(f"📝 Product Title: {product_info['product_title']}")
                print(f"Base Style: {product_info['style_id']}")
                print(f"Base Price Info:  {product_info['sale_price']} → {product_info['regular_price']}")
                print(f"Other Colorways: {len(product_info['variants'])} variants")
                deals.append(product_info)
            except Exception as e:
                print(f"⚠️ Error processing product [{idx}]:", e)
    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(deals)}")
    return deals

def get_nike_deals():
    return scrape_nike()

if __name__ == "__main__":
    deals = get_nike_deals()
    for d in deals:
        print(d)
