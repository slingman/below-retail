import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def extract_text_or_none(driver, by, value):
    try:
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((by, value)))
        return element.text.strip()
    except:
        return None


def extract_price_info(driver):
    sale_price = extract_text_or_none(driver, By.CSS_SELECTOR, '[data-testid="currentPrice-container"]')
    regular_price = extract_text_or_none(driver, By.CSS_SELECTOR, '[data-testid="initialPrice-container"]')
    return sale_price, regular_price


def parse_variant_urls(driver):
    variant_urls = []
    try:
        links = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="colorway-link"]')
        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("/t/"):
                variant_urls.append("https://www.nike.com" + href)
    except:
        pass
    return list(set(variant_urls))


def parse_product_data(driver, url):
    driver.get(url)
    time.sleep(2)

    title = extract_text_or_none(driver, By.CSS_SELECTOR, '[data-testid="product_title"]')
    style_id = extract_text_or_none(driver, By.CSS_SELECTOR, '[data-testid="product-description-style-color"]')
    if style_id and "Style:" in style_id:
        style_id = style_id.replace("Style:", "").strip()

    sale_price, regular_price = extract_price_info(driver)

    return {
        "product_title": title or "N/A",
        "style_id": style_id or "N/A",
        "sale_price": sale_price,
        "regular_price": regular_price,
        "url": url
    }


def get_nike_deals():
    print("\nFetching Nike deals...")
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_driver()
    driver.get(search_url)

    # Close cookie dialog if it exists
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(),'Accept')]"))).click()
        print("✅ Accepted cookies")
    except:
        print("ℹ️ No cookie consent dialog found")

    # Get product URLs
    product_cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
    product_urls = []
    for card in product_cards[:10]:  # Limit to first 10 to speed up
        href = card.get_attribute("href")
        if href and "/t/" in href:
            product_urls.append(href)
    product_urls = list(set(product_urls))  # Deduplicate
    print(f"🔎 Found {len(product_urls)} products on Nike search")
    print("Extracted product URLs:", product_urls)

    results = []

    for idx, url in enumerate(product_urls, 1):
        print(f"\n🔄 Processing Nike product [{idx}]...")
        try:
            product_driver = create_driver()
            base_data = parse_product_data(product_driver, url)
            print(f"📝 Product Title: {base_data['product_title']}")
            print(f"Base Style: {base_data['style_id']}")
            print(f"Base Price Info:  {base_data['sale_price']} → {base_data['regular_price']}")

            # Try to extract variant colorways
            variant_urls = parse_variant_urls(product_driver)
            print(f"Other Colorways: {len(variant_urls)} variants")
            variant_results = []

            for v_url in variant_urls:
                try:
                    variant_driver = create_driver()
                    v_data = parse_product_data(variant_driver, v_url)
                    variant_results.append(v_data)
                    variant_driver.quit()
                except Exception as e:
                    print(f"⚠️ Error parsing variant: {e}")

            print("Style Variants:")
            for v in variant_results:
                print(f" - {v['style_id']}: ${v['sale_price']} → ${v['regular_price']}")

            product_driver.quit()
            results.append({
                "base": base_data,
                "variants": variant_results
            })
        except Exception as e:
            print(f"❌ Error processing product {idx}: {e}")
            continue

    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(results)}\n")
    return results


if __name__ == "__main__":
    get_nike_deals()
