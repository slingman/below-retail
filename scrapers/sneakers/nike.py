# scrapers/sneakers/nike.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver
import time

def scrape_nike_air_max_1():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()
    driver.get(search_url)

    wait = WebDriverWait(driver, 10)
    print("Finding product links...")
    product_links = list({
        a.get_attribute("href") for a in wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay'))
        )
    })
    print(f"Found {len(product_links)} product links.\n")

    results = []

    for idx, link in enumerate(product_links, 1):
        print(f"Scraping product {idx}: {link}")
        try:
            driver.get(link)
            time.sleep(2)

            title = driver.find_element(By.CSS_SELECTOR, 'h1#pdp_product_title').text
            price_el = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]')
            current_price = price_el.text.strip()

            try:
                original_price_el = driver.find_element(By.CSS_SELECTOR, '[data-testid="initialPrice-container"]')
                original_price = original_price_el.text.strip()
            except:
                original_price = current_price

            try:
                style_info = driver.find_element(By.XPATH, '//li[contains(text(),"Style:")]').text
                style_code = style_info.split("Style:")[-1].strip()
            except:
                style_code = "Unknown Style"

            discount = ""
            try:
                if original_price != current_price:
                    original = float(original_price.replace("$", ""))
                    current = float(current_price.replace("$", ""))
                    discount_pct = round((original - current) / original * 100)
                    discount = f"{discount_pct}% off"
            except:
                pass

            results.append({
                "title": title,
                "style": style_code,
                "price": current_price,
                "original_price": original_price,
                "discount": discount,
                "url": link,
            })

        except Exception as e:
            print(f"❌ Failed to scrape {link} due to error: {e}\n")

    driver.quit()
    return results
