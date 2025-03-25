#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    base_url = "https://www.nike.com"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    deals = []

    try:
        print("📦 Fetching Nike deals...")
        driver.get(search_url)
        time.sleep(5)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@data-testid, 'product-card')]"))
            )
        except:
            print("⚠️ No product cards found.")
            return []

        product_cards = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'product-card')]")
        print(f"🔎 Found {len(product_cards)} products on Nike search")

        product_urls = []
        for card in product_cards[:10]:  # Limit to top 10
            try:
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                if link and link.startswith("https://www.nike.com/t/"):
                    product_urls.append(link)
            except Exception:
                continue

        print("Extracted product URLs:", product_urls)

        for url in product_urls:
            print(f"\n🔄 Processing Nike product: {url}")
            try:
                driver.get(url)
                time.sleep(4)

                title = driver.title.split('|')[0].strip()
                print(f"📝 Product Title: {title}")

                style_match = re.search(r'/([A-Z0-9]{6}-[0-9]{3})$', url)
                base_style = style_match.group(1) if style_match else "N/A"
                print("Base Style:", base_style)

                price_info = {"regular": None, "sale": None}
                try:
                    reg_price_el = driver.find_element(By.XPATH, "//div[contains(@data-test, 'product-price')]//div[@class='css-1emn094']")
                    price_info["regular"] = reg_price_el.text
                except:
                    pass
                try:
                    sale_price_el = driver.find_element(By.XPATH, "//div[contains(@data-test, 'product-price')]//div[@data-test='product-price-reduced']")
                    price_info["sale"] = sale_price_el.text
                except:
                    pass

                print(f"Base Price Info:  {price_info['sale']} → {price_info['regular']}")
                variants = []

                try:
                    color_els = driver.find_elements(By.XPATH, "//div[@aria-label='Color']/div/button")
                    print(f"🎨 Found {len(color_els)} colorway variants.")
                    for idx, btn in enumerate(color_els):
                        style_id = None
                        try:
                            img = btn.find_element(By.TAG_NAME, "img")
                            src = img.get_attribute("src")
                            match = re.search(r'/([A-Z0-9]{6}-[0-9]{3})', src)
                            if match:
                                style_id = match.group(1)
                        except:
                            pass

                        price_text = None
                        if style_id:
                            variant_url = f"{base_url}/t/air-max-1/{style_id}"
                            driver.get(variant_url)
                            time.sleep(4)
                            try:
                                reg = driver.find_element(By.XPATH, "//div[contains(@data-test, 'product-price')]//div[@class='css-1emn094']")
                                price_text = {"regular": reg.text}
                            except:
                                pass
                            try:
                                sale = driver.find_element(By.XPATH, "//div[@data-test='product-price-reduced']")
                                price_text["sale"] = sale.text
                            except:
                                pass

                        variants.append({
                            "style_id": style_id,
                            "price": price_text
                        })
                except:
                    print("⚠️ Failed to extract color variants.")

                print("Style Variants:")
                for v in variants:
                    reg = v["price"].get("regular") if v["price"] else None
                    sale = v["price"].get("sale") if v["price"] else None
                    discount = None
                    try:
                        if reg and sale:
                            reg_float = float(re.sub(r"[^\d.]", "", reg))
                            sale_float = float(re.sub(r"[^\d.]", "", sale))
                            discount = f"{round(100 * (reg_float - sale_float) / reg_float)}% off"
                    except:
                        pass
                    print(f" - {v['style_id']}: {sale} → {reg} ({discount})")

                deals.append({
                    "title": title,
                    "base_style": base_style,
                    "url": url,
                    "price": price_info,
                    "variants": variants
                })

            except Exception as e:
                print(f"❌ Failed to process {url}: {e}")
                traceback.print_exc()
    finally:
        driver.quit()

    print("\n✅ Nike scraping complete.")
    print("\nSUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(deals)}")
    for i, d in enumerate(deals, 1):
        print(f"{i}. {d['title']} ({d['base_style']})")

    return deals


if __name__ == "__main__":
    get_nike_deals()
