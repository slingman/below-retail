# scrapers/sneakers/nike.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from utils.selenium_setup import create_webdriver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = create_webdriver(headless=False)  # Headless off for debugging
    wait = WebDriverWait(driver, 10)

    deals = []
    print("Finding product links...")

    try:
        driver.get(NIKE_SEARCH_URL)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay')))
        product_elements = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        product_links = list({elem.get_attribute("href") for elem in product_elements})
        print(f"Found {len(product_links)} product links.")
    except Exception as e:
        print(f"Failed to fetch product links: {type(e).__name__}: {e}")
        driver.quit()
        return deals

    for idx, link in enumerate(product_links):
        print(f"\nScraping product {idx + 1}: {link}")
        try:
            driver.get(link)
            time.sleep(2)  # Let page settle

            # Title
            try:
                title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2"))).text
            except TimeoutException:
                print("❌ Could not find product title.")
                continue

            # Style ID (e.g., DV1403-600)
            try:
                style_id = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text
            except NoSuchElementException:
                style_id = "N/A"

            # Regular & Sale Price
            try:
                sale_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price-reduced"]')
                full_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                sale_price = sale_price_elem.text
                full_price = full_price_elem.text
            except NoSuchElementException:
                try:
                    full_price = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]').text
                    sale_price = None
                except NoSuchElementException:
                    full_price = "N/A"
                    sale_price = None

            print(f"Title: {title}")
            print(f"Style ID: {style_id}")
            print(f"Full Price: {full_price}")
            if sale_price:
                print(f"Sale Price: {sale_price}")

            deals.append({
                "title": title,
                "style_id": style_id,
                "price": full_price,
                "sale_price": sale_price,
                "url": link
            })

        except WebDriverException as e:
            print(f"Failed to scrape {link} due to error: {type(e).__name__}: {e}")

    driver.quit()
    return deals
