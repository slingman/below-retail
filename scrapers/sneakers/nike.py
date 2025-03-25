import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def extract_price_info(driver):
    try:
        price_container = driver.find_element(By.XPATH, "//div[contains(@class, 'price')]")
        price_text = price_container.text.strip()
        prices = re.findall(r"\$\d+\.\d{2}", price_text)
        prices = list(dict.fromkeys(prices))  # Remove duplicates
        if not prices:
            return None, None

        if len(prices) == 1:
            return float(prices[0].replace("$", "")), None  # regular price only
        else:
            sale = float(prices[0].replace("$", ""))
            original = float(prices[1].replace("$", ""))
            return sale, original
    except Exception:
        return None, None


def extract_variant_data(driver):
    variants = []
    try:
        color_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Color')]")
        print(f"🎨 Found {len(color_buttons)} colorway variants.")
        for btn in color_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)

                style_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Style:') or contains(text(),'Style #:')]"))
                )
                style_text = style_elem.text.strip()
                style_match = re.search(r"Style\s*#?:?\s*(\w+-\w+)", style_text)
                style_id = style_match.group(1) if style_match else "N/A"

                sale_price, original_price = extract_price_info(driver)
                discount = None
                if sale_price and original_price:
                    discount = round(100 * (original_price - sale_price) / original_price)

                variants.append({
                    "style": style_id,
                    "sale_price": sale_price,
                    "original_price": original_price,
                    "discount_percent": discount
                })

            except Exception as e:
                print(f"⚠️ Failed to extract variant data: {e}")
                traceback.print_exc()

    except Exception:
        print("⚠️ Could not find colorway buttons.")
    return variants


def parse_product_page(driver, url):
    try:
        driver.get(url)
        time.sleep(5)

        title = driver.title.strip().split('|')[0].strip()
        print(f"📝 Product Title: {title}")

        style_id_elem = driver.find_elements(By.XPATH, "//div[contains(text(),'Style')]")
        base_style = None
        for el in style_id_elem:
            text = el.text.strip()
            match = re.search(r"Style\s*#?:?\s*(\w+-\w+)", text)
            if match:
                base_style = match.group(1)
                break

        base_sale_price, base_original_price = extract_price_info(driver)

        variants = extract_variant_data(driver)

        return {
            "title": title,
            "url": url,
            "base_style": base_style or "N/A",
            "base_sale_price": base_sale_price,
            "base_original_price": base_original_price,
            "variants": variants
        }

    except Exception as e:
        print(f"❌ Failed to process page {url}: {e}")
        traceback.print_exc()
        return None


def get_nike_deals():
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air%20max%201&vst=air%20max%201"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    all_results = []

    try:
        print("📦 Fetching Nike deals...")
        driver.get(search_url)
        time.sleep(6)

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/t/')]"))
            )
        except:
            print("⚠️ No product links found on Nike search page.")
            return []

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/t/')]")
        product_urls = list({l.get_attribute("href").split('?')[0] for l in links if "/t/" in l.get_attribute("href")})
        print(f"🔎 Found {len(product_urls)} products on Nike search")
        print("Extracted product URLs:", product_urls[:10])

        for url in product_urls[:10]:
            print(f"\n🔄 Processing Nike product: {url}")
            result = parse_product_page(driver, url)
            if result:
                all_results.append(result)

    finally:
        driver.quit()

    return all_results


if __name__ == "__main__":
    deals = get_nike_deals()
    print("\n✅ Nike scraping complete.")
    print("\nSUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(deals)}")
    for i, d in enumerate(deals, 1):
        print(f"{i}. {d['title']} ({d['base_style']})")
