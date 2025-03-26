import time
import re
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth


def extract_price_info(driver):
    try:
        container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'product-price')]"))
        )
        text = container.text.strip()
        prices = re.findall(r"\$\d+\.\d{2}", text)
        if not prices:
            return {"regular": None, "sale": None}
        if len(prices) == 1:
            return {"regular": float(prices[0][1:]), "sale": None}
        return {"regular": float(prices[1][1:]), "sale": float(prices[0][1:])}
    except Exception:
        return {"regular": None, "sale": None}


def extract_variant_style_id(driver):
    try:
        elem = driver.find_element(By.XPATH, "//div[@data-test='product-style-color']")
        return elem.text.strip().split(":")[-1].strip()
    except Exception:
        return None


def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_driver_with_stealth()
    driver.get(search_url)
    time.sleep(8)

    deals = []

    try:
        product_links = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/t/')]"))
        )
        urls = list({elem.get_attribute("href").split("?")[0] for elem in product_links})
        print(f"🔎 Found {len(urls)} products on Nike search")
        print("Extracted product URLs:", urls[:10])

        for url in urls[:10]:  # Limit for testing
            try:
                print(f"\n🔄 Processing Nike product: {url}")
                driver.get(url)
                time.sleep(5)

                title = WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.XPATH, "//h1"))
                ).text.strip()

                base_style = extract_variant_style_id(driver)
                base_price = extract_price_info(driver)

                print(f"📝 Product Title: {title}")
                print(f"Base Style: {base_style}")
                print(f"Base Price Info:  ${base_price['sale'] or base_price['regular']} → ${base_price['regular']}")
                
                variants = []

                # find variant swatch buttons
                swatches = driver.find_elements(By.XPATH, "//div[@data-qa='colorway-container']//button")
                print(f"🎨 Found {len(swatches)} colorway variants.")

                for i, swatch in enumerate(swatches):
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", swatch)
                        time.sleep(0.3)
                        swatch.click()
                        time.sleep(3)

                        style = extract_variant_style_id(driver)
                        price = extract_price_info(driver)
                        variants.append({
                            "style": style,
                            "price": price.get("sale") or price.get("regular"),
                            "regular_price": price.get("regular"),
                            "sale_price": price.get("sale"),
                        })

                        discount_str = ""
                        if price.get("sale"):
                            discount = int(round((1 - price["sale"] / price["regular"]) * 100))
                            discount_str = f" ({discount}% off)"

                        print(f" - {style}: ${price['sale'] or price['regular']} → ${price['regular']}{discount_str}")
                    except Exception as e:
                        print(f"⚠️ Error processing variant [{i+1}]: {e}")
                        traceback.print_exc()

                deals.append({
                    "title": title,
                    "url": url,
                    "base_style": base_style,
                    "price": base_price,
                    "variants": variants
                })

            except Exception as e:
                print(f"❌ Failed to process page {url}: {e}")
                traceback.print_exc()

    finally:
        driver.quit()

    return deals
