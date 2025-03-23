#!/usr/bin/env python3
import time
import re
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for efficiency.
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1920, 1080)
    return driver

def get_nike_colorways():
    """
    Searches Nike.com for "air max 1", selects the first product,
    then extracts variant URLs from the colorway picker.
    For each variant, it extracts:
      - style_id (from the URL)
      - sale price and regular price from the price elements.
    Returns a list of dictionaries.
    """
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = init_driver()
    deals = []
    try:
        driver.get(search_url)
        time.sleep(5)  # Allow search results to load.
        # Get the first product URL.
        product_elem = driver.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay")
        prod_url = product_elem.get_attribute("href")
        print("Nike product URL:", prod_url)
        driver.get(prod_url)
        time.sleep(5)
        # Try to locate the colorway picker container.
        try:
            container = driver.find_element(By.ID, "colorway-picker-container")
            links = container.find_elements(By.TAG_NAME, "a")
            variant_urls = []
            for link in links:
                href = link.get_attribute("href")
                if href:
                    if not href.startswith("http"):
                        href = "https://www.nike.com" + href
                    variant_urls.append(href)
            print("Found", len(variant_urls), "Nike variant URLs.")
        except Exception as e:
            print("No colorway picker found; using base product URL.", e)
            variant_urls = [prod_url]
        
        # For each variant URL, extract style id and price info.
        for vurl in variant_urls:
            driver.get(vurl)
            time.sleep(5)
            style_id = vurl.rstrip("/").split("/")[-1]
            try:
                sale_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='currentPrice-container']").text.strip().replace("$", "")
            except Exception:
                sale_price = ""
            try:
                regular_price = driver.find_element(By.CSS_SELECTOR, "span[data-testid='initialPrice-container']").text.strip().replace("$", "")
            except Exception:
                regular_price = ""
            deals.append({
                "style_id": style_id,
                "sale_price": sale_price,
                "regular_price": regular_price,
                "variant_url": vurl
            })
    except Exception as e:
        print("Error in Nike scraper:", e)
        traceback.print_exc()
    finally:
        driver.quit()
    return deals

if __name__ == "__main__":
    results = get_nike_colorways()
    for r in results:
        print(r)
