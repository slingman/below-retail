#!/usr/bin/env python3
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth

def extract_price_block(driver):
    """Extracts regular and sale prices from the price block."""
    try:
        price_container = driver.find_element(By.CLASS_NAME, "product-price.is--current-price.css-s56yt7")
        spans = price_container.find_elements(By.TAG_NAME, "span")
        prices = [s.text.strip() for s in spans if "$" in s.text]
        if len(prices) == 1:
            return {"regular": float(prices[0].replace("$", "")), "sale": None}
        elif len(prices) >= 2:
            return {
                "regular": float(prices[1].replace("$", "")),
                "sale": float(prices[0].replace("$", ""))
            }
    except Exception:
        return {"regular": None, "sale": None}

def extract_colorways(driver):
    """Extracts other colorway URLs from the colorway selector section."""
    try:
        container = driver.find_element(By.CLASS_NAME, "colorways-list.css-1u0z2bu")
        links = container.find_elements(By.TAG_NAME, "a")
        color_urls = []
        for link in links:
            href = link.get_attribute("href")
            if href and "/t/" in href:
                color_urls.append(href)
        return list(set(color_urls))
    except Exception:
        return []

def parse_product_page(driver, url):
    """Extracts all info for a given product page."""
    driver.get(url)
    time.sleep(5)

    # Title
    try:
        title_elem = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "headline-5.css-zvhuxb"))
        )
        title = title_elem.text.strip()
    except Exception:
        title = "N/A"

    # Style ID
    try:
        style_elem = driver.find_element(By.XPATH, "//div[contains(text(),'Style') or contains(text(),'Product')]")
        style_id = style_elem.text.split(":")[-1].strip()
    except Exception:
        style_id = "N/A"

    # Price info
    prices = extract_price_block(driver)

    return {
        "title": title,
        "style_id": style_id,
        "url": url,
        "price": prices
    }

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_driver_with_stealth()
    driver.get(search_url)
    time.sleep(6)

    try:
        product_cards = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__link-overlay"))
        )
        product_urls = list({card.get_attribute("href") for card in product_cards if "/t/" in card.get_attribute("href")})
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls[:10])
    except Exception as e:
        print("❌ Failed to extract product cards:", e)
        traceback.print_exc()
        driver.quit()
        return []

    all_products = []

    for idx, url in enumerate(product_urls[:10], start=1):
        try:
            print(f"\n🔄 Processing Nike product: {url}")
            product_data = parse_product_page(driver, url)

            # Try finding colorway variants
            variant_urls = extract_colorways(driver)
            variants = []

            if variant_urls:
                print(f"🎨 Found {len(variant_urls)} colorway variants.")
                for vu in variant_urls:
                    if vu == url:
                        continue  # Skip base URL
                    try:
                        variant_data = parse_product_page(driver, vu)
                        variants.append(variant_data)
                    except Exception as ve:
                        print(f"⚠️ Failed to process variant: {vu}")
                        traceback.print_exc()
            else:
                print("🎨 Found 0 colorway variants.")

            product_data["variants"] = variants
            all_products.append(product_data)

        except Exception as e:
            print(f"❌ Error scraping product {url}: {e}")
            traceback.print_exc()

    driver.quit()
    return all_products

if __name__ == "__main__":
    products = get_nike_deals()
    print("\n✅ Nike scraping complete.")
    print(f"\nSUMMARY RESULTS:\nTotal unique Nike products: {len(products)}")
    for idx, p in enumerate(products, 1):
        print(f"{idx}. {p['title']} ({p['style_id']})")
        if p["price"]:
            print(f"   💵 ${p['price']}")
        if p.get("variants"):
            for v in p["variants"]:
                reg = v['price'].get("regular")
                sale = v['price'].get("sale")
                if sale:
                    pct = round(100 * (reg - sale) / reg)
                    print(f"     - {v['style_id']}: ${sale} → ${reg} ({pct}% off)")
                else:
                    print(f"     - {v['style_id']}: ${reg}")
