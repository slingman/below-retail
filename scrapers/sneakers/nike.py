import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def extract_price_info(driver):
    try:
        current = driver.find_element(By.CSS_SELECTOR, "[data-testid='currentPrice-container']").text
    except:
        current = None
    try:
        original = driver.find_element(By.CSS_SELECTOR, "[data-testid='initialPrice-container']").text
    except:
        original = None
    try:
        discount = driver.find_element(By.CSS_SELECTOR, "[data-testid='OfferPercentage']").text
    except:
        discount = None
    return current, original, discount

def extract_title(driver):
    try:
        return driver.find_element(By.CSS_SELECTOR, "[data-testid='product_title']").text
    except:
        return "N/A"

def extract_style_id(driver):
    try:
        style_line = driver.find_element(By.XPATH, "//li[contains(text(), 'Style:')]").text
        match = re.search(r"Style:\s+([A-Z0-9\-]+)", style_line)
        return match.group(1) if match else "N/A"
    except:
        return "N/A"

def parse_product_page(driver, url):
    try:
        driver.get(url)
        time.sleep(2)
        title = extract_title(driver)
        base_style = extract_style_id(driver)
        current, original, discount = extract_price_info(driver)

        print(f"📝 Product Title: {title}")
        print(f"Base Style: {base_style}")
        print(f"Base Price Info:  {current} → {original}")

        # Find variant URLs (re-fetch to avoid stale refs)
        variant_urls = set()
        try:
            colorway_links = driver.find_elements(By.CSS_SELECTOR, "a[data-testid^='colorway-link']")
            for link in colorway_links:
                try:
                    href = link.get_attribute("href")
                    if href and href.startswith("http"):
                        variant_urls.add(href)
                except Exception as e:
                    print(f"⚠️ Error accessing link: {e}")
        except Exception as e:
            print(f"⚠️ Could not extract variants: {e}")

        print(f"Other Colorways: {len(variant_urls)} variants")

        variant_data = []
        for vurl in variant_urls:
            try:
                driver.get(vurl)
                time.sleep(1.5)
                v_style = extract_style_id(driver)
                v_current, v_original, v_discount = extract_price_info(driver)
                variant_data.append({
                    "style": v_style,
                    "current_price": v_current,
                    "original_price": v_original,
                    "discount": v_discount,
                    "url": vurl
                })
            except Exception as e:
                print(f"⚠️ Error processing variant: {vurl} — {e}")
        
        return {
            "title": title,
            "base_style": base_style,
            "price": current,
            "original_price": original,
            "discount": discount,
            "variants": variant_data
        }
    except Exception as e:
        print(f"❌ Failed to process page {url}: {e}")
        traceback.print_exc()
        return None

def scrape_nike():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_driver()
    driver.get(search_url)
    time.sleep(3)

    try:
        print("Fetching Nike deals...")
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Accept')]"))
            ).click()
            print("✅ Clicked cookie consent")
        except:
            print("ℹ️ No cookie consent dialog found")

        product_cards = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='product-card__img-link-overlay']")
        product_urls = [card.get_attribute("href") for card in product_cards if card.get_attribute("href")]
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls[:10])

        all_results = []
        for url in product_urls[:10]:  # Limit to first 10 products
            print(f"\n🔄 Processing Nike product: {url}")
            data = parse_product_page(driver, url)
            if data:
                print("Style Variants:")
                for v in data["variants"]:
                    print(f" - {v['style']}: {v['current_price']} → {v['original_price']} ({v['discount']})")
                all_results.append(data)
        return all_results

    finally:
        driver.quit()

def get_nike_deals():
    return scrape_nike()

if __name__ == "__main__":
    deals = get_nike_deals()
    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(deals)}")
