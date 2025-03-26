#!/usr/bin/env python3
import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver_with_stealth

def parse_product_page(driver, url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        time.sleep(2)

        title = driver.title.replace(" . Nike.com", "").strip()
        print(f"📝 Product Title: {title}")

        # Try to extract base style ID from the URL
        try:
            base_style = url.split("/")[-1].split("?")[0]
        except Exception:
            base_style = "N/A"

        # Try to get price info
        try:
            price_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'product-price')]"))
            )
            price_text = price_div.text.strip().replace("\n", " ")
        except:
            price_text = "None"

        print(f"Base Style: {base_style}")
        print(f"Base Price Info:  ${price_text}")
        print("🎨 Found 0 colorway variants.\n")
        return {
            "title": title,
            "base_style": base_style,
            "price_info": price_text,
            "variants": []
        }

    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
        traceback.print_exc()
        return None

def get_nike_deals():
    print("📦 Fetching Nike deals...")

    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_driver_with_stealth()

    deals = []

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
        time.sleep(5)

        product_links = list(set([
            a.get_attribute("href")
            for a in driver.find_elements(By.XPATH, "//a[contains(@href, '/t/')]")
            if "/t/" in a.get_attribute("href")
        ]))

        print(f"🔎 Found {len(product_links)} products on Nike search")
        print("Extracted product URLs:", product_links[:10])  # Limit to 10 for sanity

        for url in product_links[:10]:
            result = parse_product_page(driver, url)
            if result:
                deals.append(result)

    except Exception as e:
        print("❌ Failed to fetch Nike deals:", e)
        traceback.print_exc()

    finally:
        driver.quit()

    print("✅ Nike scraping complete.\n")
    print("SUMMARY RESULTS:")
    print(f"Total unique Nike products: {len(deals)}")
    for i, d in enumerate(deals, 1):
        print(f"{i}. {d['title']} ({d['base_style']})")
        print(f"   💵 ${d['price_info']}")
    return deals

if __name__ == "__main__":
    get_nike_deals()
