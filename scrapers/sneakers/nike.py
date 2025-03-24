#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def get_element_text(driver, by, value, timeout=6):
    try:
        elem = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return elem.text.strip()
    except Exception:
        return "N/A"

def extract_price_info(driver):
    current = get_element_text(driver, By.XPATH, "//div[@id='price-container']//span[@data-testid='currentPrice-container']")
    regular = get_element_text(driver, By.XPATH, "//div[@id='price-container']//span[@data-testid='initialPrice-container']")
    discount = get_element_text(driver, By.XPATH, "//div[@id='price-container']//span[@data-testid='OfferPercentage']")
    return current, regular, discount

def extract_style_id(driver):
    try:
        li = driver.find_element(By.XPATH, "//li[contains(text(),'Style:')]")
        return li.text.split("Style:")[-1].strip()
    except:
        return "N/A"

def extract_variant_urls(driver):
    links = []
    try:
        colorway_elements = driver.find_elements(By.XPATH, "//div[@id='colorway-picker-container']//a[@data-testid and contains(@href, '/t/')]")
        for elem in colorway_elements:
            href = elem.get_attribute("href")
            if href and href.startswith("https://www.nike.com"):
                links.append(href)
    except Exception:
        pass
    return list(set(links))

def parse_product_page(driver, url):
    data = []
    try:
        driver.get(url)
        time.sleep(2)
        title = get_element_text(driver, By.XPATH, "//h1[@data-testid='product_title']")
        base_style = extract_style_id(driver)
        current_price, regular_price, discount = extract_price_info(driver)
        base_info = {
            "product_url": url,
            "title": title,
            "style_id": base_style,
            "price": current_price,
            "regular_price": regular_price,
            "discount": discount,
            "is_base_product": True
        }
        data.append(base_info)

        # Extract and visit colorway variants
        variant_urls = extract_variant_urls(driver)
        print(f"🟢 Found {len(variant_urls)} colorways")
        for link in variant_urls:
            if link == url:
                continue  # skip base
            try:
                driver.get(link)
                time.sleep(2)
                variant_title = get_element_text(driver, By.XPATH, "//h1[@data-testid='product_title']")
                variant_style = extract_style_id(driver)
                v_price, v_regular, v_discount = extract_price_info(driver)
                data.append({
                    "product_url": link,
                    "title": variant_title,
                    "style_id": variant_style,
                    "price": v_price,
                    "regular_price": v_regular,
                    "discount": v_discount,
                    "is_base_product": False
                })
            except Exception as e:
                print(f"⚠️ Failed to process variant: {link}")
                traceback.print_exc()
    except Exception as e:
        print(f"❌ Failed to parse base product: {url}")
        traceback.print_exc()
    return data

def get_nike_deals():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_driver()
    all_deals = []
    try:
        driver.get(search_url)
        time.sleep(3)
        print("ℹ️ No cookie consent dialog found")
        product_links = []
        cards = driver.find_elements(By.XPATH, "//a[contains(@href, '/t/') and contains(@class, 'product-card__img-link-overlay')]")
        for card in cards:
            href = card.get_attribute("href")
            if href and href.startswith("https://www.nike.com/t/") and href not in product_links:
                product_links.append(href)
        print(f"🔎 Found {len(product_links)} products on Nike search")
        print("Extracted product URLs:", product_links[:10])
        product_links = product_links[:10]  # limit for dev

        for i, url in enumerate(product_links, 1):
            print(f"\n🔄 Processing Nike product [{i}]...")
            deals = parse_product_page(driver, url)
            all_deals.extend(deals)
    finally:
        driver.quit()

    print("\nSUMMARY RESULTS:")
    print(f"Total Nike deals processed: {len(all_deals)}")
    return all_deals

if __name__ == "__main__":
    deals = get_nike_deals()
    for deal in deals:
        print(deal)
