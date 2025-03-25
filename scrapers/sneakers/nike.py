#!/usr/bin/env python3
import time
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
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def parse_product_page(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        product = {}

        # Get product title
        try:
            title_elem = driver.find_element(By.XPATH, "//h1")
            product["product_title"] = title_elem.text.strip()
        except:
            product["product_title"] = "N/A"

        # Get base style
        try:
            base_style = url.split("/")[-1]
            product["style_id"] = base_style
        except:
            product["style_id"] = "N/A"

        # Get base price and sale price
        try:
            price_final = driver.find_element(By.XPATH, "//div[contains(@data-test, 'product-price')]//div").text
            price_parts = price_final.split("$")
            prices = [p for p in price_parts if p.strip()]
            if len(prices) == 2:
                product["sale_price"] = f"${prices[0]}"
                product["regular_price"] = f"${prices[1]}"
            elif len(prices) == 1:
                product["sale_price"] = None
                product["regular_price"] = f"${prices[0]}"
        except:
            product["sale_price"] = None
            product["regular_price"] = None

        # Find all variants in the color selector (swatches)
        try:
            swatches = driver.find_elements(By.CSS_SELECTOR, '[data-qa="colorway-selector-swatch"]')
            product["variants"] = []
            for swatch in swatches:
                try:
                    variant_style = swatch.get_attribute("data-style-color")
                    swatch.click()
                    time.sleep(3)

                    price = driver.find_element(By.XPATH, "//div[contains(@data-test, 'product-price')]//div").text
                    price_parts = price.split("$")
                    price_values = [p for p in price_parts if p.strip()]
                    variant_price = f"${price_values[0]}" if len(price_values) >= 1 else None
                    variant_sale = f"${price_values[1]}" if len(price_values) == 2 else None

                    product["variants"].append({
                        "style_id": variant_style,
                        "price": variant_price,
                        "sale_price": variant_sale
                    })
                except Exception:
                    continue
        except:
            product["variants"] = []

        return product
    except Exception as e:
        print(f"❌ Failed to process page {url}: {e}")
        traceback.print_exc()
        return None


def get_nike_deals():
    driver = create_driver()
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver.get(search_url)
    time.sleep(6)

    deals = []

    try:
        product_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/t/')]")
        urls = list(dict.fromkeys([link.get_attribute("href") for link in product_links if "/t/" in link.get_attribute("href")]))
        urls = [u for u in urls if "air-max" in u]
        print(f"🔎 Found {len(urls)} products on Nike search")
        print("Extracted product URLs:", urls[:10])

        for url in urls[:10]:
            print(f"\n🔄 Processing Nike product: {url}")
            product_data = parse_product_page(driver, url)
            if product_data:
                print(f"📝 Product Title: {product_data['product_title']}")
                print(f"Base Style: {product_data['style_id']}")
                base_price = product_data.get("sale_price") or product_data.get("regular_price")
                print(f"Base Price Info:  {product_data.get('sale_price')} → {product_data.get('regular_price')}")
                print(f"Other Colorways: {len(product_data.get('variants', []))} variants")
                print("Style Variants:")
                for v in product_data.get("variants", []):
                    print(f" - {v['style_id']}: {v['price']} → {v['sale_price']}")
                deals.append(product_data)

    except Exception as e:
        print("⚠️ Error during Nike scraping:", e)
        traceback.print_exc()
    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(deals)}")
    return deals


if __name__ == "__main__":
    get_nike_deals()
