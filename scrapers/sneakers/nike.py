import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth


def extract_style_id_from_url(url: str) -> str:
    return url.split("/")[-1].split("?")[0].upper()


def extract_price_block(driver):
    try:
        price_block = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@data-test, 'product-price')]"))
        )
        price_text = price_block.text.strip().replace("\n", " ")
        prices = re.findall(r"\$[\d,.]+", price_text)
        if len(prices) == 2:
            return {"regular": prices[1], "sale": prices[0]}
        elif len(prices) == 1:
            return {"regular": prices[0], "sale": None}
        else:
            return {"regular": None, "sale": None}
    except Exception:
        return {"regular": None, "sale": None}


def parse_product_page(driver, url):
    product_data = {}
    driver.get(url)
    time.sleep(5)

    try:
        title_elem = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, "//h1"))
        )
        product_data["title"] = title_elem.text.strip()
    except Exception:
        product_data["title"] = None

    base_style = extract_style_id_from_url(url)
    product_data["base_style"] = base_style

    product_data["price"] = extract_price_block(driver)
    product_data["variants"] = []

    try:
        swatches = driver.find_elements(By.XPATH, "//div[@data-testid='colorwayPicker']//button")
        print(f"🎨 Found {len(swatches)} colorway variants.")
        for idx, swatch in enumerate(swatches):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", swatch)
                driver.execute_script("arguments[0].click();", swatch)
                time.sleep(3)

                style_id = extract_style_id_from_url(driver.current_url)
                price = extract_price_block(driver)

                discount = None
                if price["sale"] and price["regular"]:
                    try:
                        r = float(price["regular"].replace("$", "").replace(",", ""))
                        s = float(price["sale"].replace("$", "").replace(",", ""))
                        discount = round((r - s) / r * 100)
                    except Exception:
                        pass

                product_data["variants"].append({
                    "style": style_id,
                    "price": price,
                    "discount_percent": discount
                })

            except Exception as e:
                print(f"⚠️ Failed to process variant #{idx+1}: {e}")

    except Exception:
        print("⚠️ No colorway variants found.")
    return product_data


def get_nike_deals():
    url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_driver_with_stealth()
    driver.get(url)
    time.sleep(5)

    deals = []

    try:
        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/t/')]"))
        )
        product_links = []
        for card in cards:
            href = card.get_attribute("href")
            if href and "/t/" in href and href not in product_links:
                product_links.append(href)

        print(f"🔎 Found {len(product_links)} products on Nike search")
        print("Extracted product URLs:", product_links[:10])

        for url in product_links[:10]:
            print(f"\n🔄 Processing Nike product: {url}")
            try:
                data = parse_product_page(driver, url)
                deals.append(data)
            except Exception as e:
                print(f"❌ Failed to parse Nike product: {e}")

    finally:
        driver.quit()

    return deals
