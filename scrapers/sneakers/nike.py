# scrapers/sneakers/nike.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver

def scrape_nike_air_max_1():
    deals = []
    base_url = "https://www.nike.com"
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

    driver = create_webdriver()
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-card__link-overlay"))
        )
    except Exception as e:
        print(f"❌ Could not load search results: {e}")
        driver.quit()
        return deals

    product_links = list({
        link.get_attribute("href")
        for link in driver.find_elements(By.CLASS_NAME, "product-card__link-overlay")
    })

    print(f"Found {len(product_links)} product links.\n")

    for idx, link in enumerate(product_links, 1):
        print(f"Scraping product {idx}: {link}")
        try:
            if "air-max-1" not in link.lower():
                continue

            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "pdp_product_title"))
            )

            title = driver.find_element(By.ID, "pdp_product_title").text.strip()
            price_container = driver.find_element(By.ID, "price-container")

            try:
                current_price = price_container.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text
                current_price = float(current_price.replace("$", ""))
            except:
                current_price = None

            try:
                original_price = price_container.find_element(By.CSS_SELECTOR, '[data-testid="initialPrice-container"]').text
                original_price = float(original_price.replace("$", ""))
            except:
                original_price = current_price

            try:
                style_line = driver.find_element(By.XPATH, '//li[@data-testid="product-description-style-color"]').text
                style_id = style_line.split("Style:")[-1].strip()
            except:
                style_id = "N/A"

            discount_pct = 0
            if original_price and current_price and original_price > current_price:
                discount_pct = round((original_price - current_price) / original_price * 100)

            deals.append({
                "title": title,
                "style_id": style_id,
                "current_price": current_price,
                "original_price": original_price,
                "discount_pct": discount_pct,
                "url": link
            })

        except Exception as e:
            print(f"❌ Failed to scrape {link} due to error: {e}\n")

    driver.quit()
    return deals
