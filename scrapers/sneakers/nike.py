import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.selenium_setup import get_chrome_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 15)
    results = []

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(3)

        product_links = []
        cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        for card in cards:
            href = card.get_attribute("href")
            if href and href not in product_links:
                product_links.append(href)

        print(f"Found {len(product_links)} product links.\n")

        for link in product_links:
            try:
                driver.get(link)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-2')))

                # Title
                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text.strip()
                except NoSuchElementException:
                    title = "N/A"

                # Style ID
                try:
                    style_id = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
                except NoSuchElementException:
                    style_id = "N/A"

                # Prices
                try:
                    sale_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price-reduced"]').text.strip()
                except NoSuchElementException:
                    sale_price = None

                try:
                    regular_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]').text.strip()
                except NoSuchElementException:
                    regular_price = sale_price if sale_price else "N/A"

                if not sale_price:
                    sale_price = regular_price

                print(f"{title} ({style_id})")
                print(f"  Price: {sale_price} (was {regular_price})")
                print(f"  Variants: 0\n")

                results.append({
                    "title": title,
                    "style_id": style_id,
                    "price": regular_price,
                    "sale_price": sale_price,
                    "variants": []
                })

            except Exception as e:
                print(f"Failed to scrape {link} due to error: {e}\n")
                continue

    finally:
        driver.quit()

    return results
