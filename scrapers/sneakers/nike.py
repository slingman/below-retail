import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.selenium_setup import get_driver_with_stealth

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def extract_price_info(driver):
    try:
        price_container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-price"]'))
        )
        price_text = price_container.text.strip().replace("\n", " ")
        prices = price_text.replace("$", "").split(" ")
        if len(prices) == 2:
            sale_price = float(prices[0])
            regular_price = float(prices[1])
        else:
            sale_price = None
            regular_price = float(prices[0])
        return {
            "regular": regular_price,
            "sale": sale_price,
        }
    except:
        return {"regular": None, "sale": None}

def extract_style_id_from_url(url):
    return url.split("/")[-1]

def get_nike_deals():
    deals = []
    driver = get_driver_with_stealth()
    driver.get(NIKE_SEARCH_URL)
    time.sleep(5)

    product_cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
    product_urls = [a.get_attribute("href") for a in product_cards][:10]
    print(f"🔎 Found {len(product_urls)} products on Nike search")
    print("Extracted product URLs:", product_urls)

    for url in product_urls:
        try:
            print(f"\n🔄 Processing Nike product: {url}")
            driver.get(url)
            time.sleep(5)

            try:
                title_elem = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='product-title']"))
                )
                title = title_elem.text.strip()
            except:
                title = "N/A"

            style_id = extract_style_id_from_url(url)
            price_info = extract_price_info(driver)

            print(f"📝 Product Title: {title}")
            print(f"Base Style: {style_id}")
            print(f"Base Price Info:  ${price_info['sale']} → ${price_info['regular']}")

            # Check for colorway variants (they are buttons with data-style-color)
            variant_buttons = driver.find_elements(By.CSS_SELECTOR, "button.css-1pe4hfj[data-style-color]")
            variant_ids = [btn.get_attribute("data-style-color") for btn in variant_buttons]
            print(f"🎨 Found {len(variant_ids)} colorway variants.")

            variants = []
            for var_id in variant_ids:
                variant_url = f"https://www.nike.com/t/air-max-1/{var_id}"
                try:
                    driver.get(variant_url)
                    time.sleep(5)
                    var_price_info = extract_price_info(driver)
                    variants.append({
                        "style_id": var_id,
                        "regular_price": var_price_info["regular"],
                        "sale_price": var_price_info["sale"],
                    })
                except Exception:
                    continue

            deals.append({
                "title": title,
                "style_id": style_id,
                "price_info": price_info,
                "variants": variants,
                "url": url
            })

        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")
            traceback.print_exc()
            continue

    driver.quit()
    return deals
