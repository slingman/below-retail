import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from utils.selenium_setup import get_chrome_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 15)
    results = []

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(3)

        cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        product_links = list({card.get_attribute("href") for card in cards if card.get_attribute("href")})

        print(f"Found {len(product_links)} product links.\n")

        for link in product_links:
            try:
                driver.get(link)
                time.sleep(2)  # Give React some room to breathe

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="product-style-colorway"]')))

                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text.strip()
                except:
                    title = "N/A"

                try:
                    style_id = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
                except:
                    style_id = "N/A"

                try:
                    sale_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price-reduced"]')
                    sale_price = sale_price_elem.text.strip()
                except NoSuchElementException:
                    sale_price = None

                try:
                    regular_price_elem = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
                    regular_price = regular_price_elem.text.strip()
                except NoSuchElementException:
                    regular_price = sale_price or "N/A"

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

                time.sleep(1)

            except WebDriverException as e:
                print(f"Failed to scrape {link} due to error: {e.msg}\n")
                continue

    finally:
        driver.quit()

    return results
