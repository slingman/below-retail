#!/usr/bin/env python3
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    )
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    deals = []
    try:
        driver.get(search_url)
        time.sleep(5)

        product_links = list(
            set(
                elem.get_attribute("href")
                for elem in driver.find_elements(By.XPATH, "//a[contains(@href, '/t/air-max-1')]")
                if elem.get_attribute("href")
            )
        )

        print(f"🔎 Found {len(product_links)} products on Nike search")
        print("Extracted product URLs:", product_links[:10])

        for url in product_links[:10]:
            print(f"\n🔄 Processing Nike product: {url}")
            driver.get(url)
            time.sleep(4)

            try:
                title = driver.find_element(By.XPATH, "//h1").text.strip()
            except:
                title = "N/A"

            try:
                style_id = driver.find_element(By.XPATH, "//div[contains(text(),'Style:')]").text.split("Style:")[-1].strip()
            except:
                style_id = "N/A"

            try:
                price_container = driver.find_element(By.XPATH, "//div[@data-test='product-price']")
                price_text = price_container.text.strip().replace("\n", " ")
                prices = re.findall(r"\$[\d\.]+", price_text)
                if len(prices) == 2:
                    sale_price = prices[0]
                    regular_price = prices[1]
                elif len(prices) == 1:
                    sale_price = None
                    regular_price = prices[0]
                else:
                    sale_price = regular_price = None
            except:
                sale_price = regular_price = None

            print(f"📝 Product Title: {title}")
            print(f"Base Style: {style_id}")
            print(f"Base Price Info:  {f'${sale_price} → ${regular_price}' if sale_price else f'${regular_price}'}")

            # Look for other colorways
            colorway_data = []
            try:
                thumb_buttons = driver.find_elements(By.XPATH, "//li[contains(@class,'colorway')]//button")
                print(f"🎨 Found {len(thumb_buttons)} colorway variants.")
                for i in range(len(thumb_buttons)):
                    try:
                        thumb_buttons = driver.find_elements(By.XPATH, "//li[contains(@class,'colorway')]//button")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumb_buttons[i])
                        thumb_buttons[i].click()
                        time.sleep(3)

                        style = driver.find_element(By.XPATH, "//div[contains(text(),'Style:')]").text.split("Style:")[-1].strip()
                        price_container = driver.find_element(By.XPATH, "//div[@data-test='product-price']")
                        price_text = price_container.text.strip().replace("\n", " ")
                        prices = re.findall(r"\$[\d\.]+", price_text)
                        if len(prices) == 2:
                            variant_sale = prices[0]
                            variant_regular = prices[1]
                        elif len(prices) == 1:
                            variant_sale = None
                            variant_regular = prices[0]
                        else:
                            variant_sale = variant_regular = None

                        discount = None
                        if variant_sale and variant_regular:
                            try:
                                discount = round(100 * (1 - float(variant_sale) / float(variant_regular)))
                            except:
                                pass

                        colorway_data.append({
                            "style_id": style,
                            "regular_price": variant_regular,
                            "sale_price": variant_sale,
                            "discount": discount,
                        })
                    except Exception as e:
                        print(f"⚠️ Failed to extract variant {i+1}: {e}")
            except:
                print("🎨 No colorway variants found.")

            deals.append({
                "store": "Nike",
                "product_url": url,
                "title": title,
                "base_style": style_id,
                "regular_price": regular_price,
                "sale_price": sale_price,
                "variants": colorway_data
            })

    finally:
        driver.quit()

    return deals


if __name__ == "__main__":
    print("📦 Fetching Nike deals...")
    results = get_nike_deals()
    print("\n✅ Nike scraping complete.\n")
    print("SUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(results)}")
    for i, prod in enumerate(results, 1):
        print(f"{i}. {prod['title']} ({prod['base_style']})")
        print(f"   💵 ${prod['sale_price']} → ${prod['regular_price']}" if prod['sale_price'] else f"   💵 ${prod['regular_price']}")
        for v in prod["variants"]:
            discount = f" ({v['discount']}% off)" if v["discount"] else ""
            print(f"      🔹 {v['style_id']}: ${v['sale_price']} → ${v['regular_price']}{discount}")
