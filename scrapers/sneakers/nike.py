import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth

BASE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def get_text_safe(driver, selector, by=By.XPATH):
    try:
        return driver.find_element(by, selector).text.strip()
    except Exception:
        return None

def extract_price_block(driver):
    try:
        regular = get_text_safe(driver, "//div[@data-test='product-price']//div[contains(@class,'is--striked-out')]")
        sale = get_text_safe(driver, "//div[@data-test='product-price']//div[contains(@class,'is--current-price')]")
        if not regular:  # No discount
            regular = sale
            sale = None
        return {"regular": regular, "sale": sale}
    except Exception:
        return {"regular": None, "sale": None}

def get_nike_deals():
    driver = get_driver_with_stealth()
    wait = WebDriverWait(driver, 10)
    print("📦 Fetching Nike deals...")

    driver.get(BASE_SEARCH_URL)
    time.sleep(3)

    product_links = set()
    try:
        product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__img-link-overlay")))
        for card in product_cards:
            href = card.get_attribute("href")
            if href:
                product_links.add(href)
    except Exception:
        print("❌ Failed to find product cards")

    print(f"🔎 Found {len(product_links)} products on Nike search")
    print("Extracted product URLs:", list(product_links)[:10])

    deals = []

    for url in list(product_links):
        print(f"\n🔄 Processing Nike product: {url}")
        try:
            driver.get(url)
            time.sleep(2)

            title = get_text_safe(driver, "//h1") or "None"
            base_style = url.split("/")[-1].strip()
            price_block = extract_price_block(driver)
            print(f"📝 Product Title: {title}")
            print(f"Base Style: {base_style}")
            print(f"Base Price Info:  ${price_block['sale'] or price_block['regular']}")
            
            variant_links = set()
            try:
                color_buttons = driver.find_elements(By.CSS_SELECTOR, "div.css-xf3ahq a")  # variant colorway buttons
                for btn in color_buttons:
                    href = btn.get_attribute("href")
                    if href and "nike.com" in href:
                        variant_links.add(href)
            except Exception:
                pass

            print(f"🎨 Found {len(variant_links)} colorway variants.")

            variant_data = []

            for variant_url in variant_links:
                try:
                    driver.get(variant_url)
                    time.sleep(2)

                    variant_title = get_text_safe(driver, "//h1")
                    style_id = variant_url.split("/")[-1].strip()
                    variant_price = extract_price_block(driver)
                    variant_data.append({
                        "style_id": style_id,
                        "title": variant_title,
                        "price": variant_price
                    })

                    print(f"→ Variant: {style_id} | Title: {variant_title} | Price: {variant_price}")
                except Exception as ve:
                    print(f"⚠️ Failed to extract variant: {variant_url} — {ve}")

            deals.append({
                "title": title,
                "style_id": base_style,
                "price": price_block,
                "url": url,
                "variants": variant_data
            })

        except Exception as e:
            print(f"❌ Failed to process product page: {e}")
            continue

    driver.quit()
    print("\n✅ Nike scraping complete.")
    print("\nSUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(deals)}")
    for idx, deal in enumerate(deals, start=1):
        print(f"{idx}. {deal['title']} ({deal['style_id']})")
        print(f"   💵 {deal['price']}")
        for variant in deal['variants']:
            print(f"   🎨 {variant['style_id']} — {variant['price']}")
    return deals
