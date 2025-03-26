import time
import re
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth


def extract_price_info(driver):
    try:
        price_containers = driver.find_elements(By.XPATH, "//div[contains(@class,'product-price')]")
        for container in price_containers:
            text = container.text.strip()
            matches = re.findall(r"\$\d+\.\d{2}", text)
            if matches:
                prices = list(map(lambda x: float(x[1:]), matches))
                if len(prices) == 1:
                    return {"regular": prices[0], "sale": None}
                elif len(prices) == 2:
                    return {"regular": prices[1], "sale": prices[0]}
        return {"regular": None, "sale": None}
    except Exception:
        return {"regular": None, "sale": None}


def extract_variant_info(driver):
    variants = []
    try:
        buttons = driver.find_elements(By.XPATH, "//div[@data-qa='colorway-container']//button")
        print(f"🎨 Found {len(buttons)} colorway variants.")

        for idx, btn in enumerate(buttons):
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                btn.click()
                time.sleep(3)

                style_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@data-test='product-style-color']"))
                )
                style = style_elem.text.strip().split(":")[-1].strip()

                price_info = extract_price_info(driver)

                variants.append({
                    "style": style,
                    "price": price_info.get("sale") or price_info.get("regular"),
                    "regular_price": price_info.get("regular"),
                    "sale_price": price_info.get("sale")
                })
            except Exception as e:
                print(f"⚠️ Failed to process variant [{idx+1}]: {e}")
                traceback.print_exc()
                continue
    except Exception as e:
        print(f"⚠️ Failed to extract variants: {e}")
        traceback.print_exc()
    return variants


def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_driver_with_stealth()
    driver.get(search_url)
    time.sleep(8)

    results = []

    try:
        product_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/t/')]"))
        )
        urls = list({card.get_attribute("href").split("?")[0] for card in product_cards})
        print(f"🔎 Found {len(urls)} products on Nike search")
        print("Extracted product URLs:", urls[:10])

        for url in urls[:10]:  # Limit for testing
            try:
                print(f"\n🔄 Processing Nike product: {url}")
                driver.get(url)
                time.sleep(5)

                try:
                    title = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//h1"))
                    ).text.strip()
                except:
                    title = "N/A"

                try:
                    style = driver.find_element(By.XPATH, "//div[@data-test='product-style-color']").text.strip().split(":")[-1].strip()
                except:
                    style = "N/A"

                price_info = extract_price_info(driver)
                variants = extract_variant_info(driver)

                results.append({
                    "title": title,
                    "url": url,
                    "base_style": style,
                    "price": price_info,
                    "variants": variants,
                })

                print(f"📝 Product Title: {title}")
                print(f"Base Style: {style}")
                print(f"Base Price Info:  ${price_info.get('sale') or price_info.get('regular')}")
                print(f"Style Variants:")
                for v in variants:
                    print(f" - {v['style']}: ${v['sale_price'] or v['price']} → ${v['regular_price']}")

            except Exception as e:
                print(f"❌ Failed to process page {url}: {e}")
                traceback.print_exc()
                continue

    finally:
        driver.quit()

    return results
