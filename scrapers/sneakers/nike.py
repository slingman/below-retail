# scrapers/sneakers/nike.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from utils.selenium_setup import get_chrome_driver
import time

def scrape_nike_air_max_1():
    url = 'https://www.nike.com/w?q=air%20max%201&vst=air%20max%201'
    driver = get_chrome_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        product_cards = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'a.product-card__link-overlay')
        ))
    except TimeoutException:
        print("Timeout: Could not find product cards.")
        driver.quit()
        return []

    product_links = list({card.get_attribute('href') for card in product_cards if card.get_attribute('href')})
    print(f"Found {len(product_links)} product links.")

    all_products = []

    for link in product_links:
        driver.get(link)
        time.sleep(2)  # buffer for product page content to load

        try:
            title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text
        except:
            title = "N/A"

        try:
            base_style = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-color"]').text
        except:
            base_style = "N/A"

        try:
            price_block = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
            regular_price = price_block.find_element(By.CSS_SELECTOR, '[data-test="original-price"]').text
            sale_price = price_block.find_element(By.CSS_SELECTOR, '[data-test="sale-price"]').text
        except:
            try:
                sale_price = None
                regular_price = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]').text
            except:
                regular_price = "N/A"
                sale_price = None

        print(f"\n{title} ({base_style})")
        print(f"  Price: {regular_price}" + (f" → {sale_price}" if sale_price else ""))

        variants = []
        try:
            color_buttons = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '[data-test="colorway-thumbnails"] button')
            ))
        except TimeoutException:
            color_buttons = []

        for btn in color_buttons:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                btn.click()
                time.sleep(1)

                style = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-color"]').text

                try:
                    price_block = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                    regular = price_block.find_element(By.CSS_SELECTOR, '[data-test="original-price"]').text
                    sale = price_block.find_element(By.CSS_SELECTOR, '[data-test="sale-price"]').text
                except:
                    try:
                        sale = None
                        regular = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]').text
                    except:
                        regular = "N/A"
                        sale = None

                variants.append({
                    'style_id': style,
                    'regular_price': regular,
                    'sale_price': sale
                })

            except StaleElementReferenceException:
                continue
            except:
                continue

        print(f"  Variants: {len(variants)}")
        for v in variants:
            line = f"    {v['style_id']} — {v['regular_price']}"
            if v['sale_price']:
                line += f" → {v['sale_price']}"
            print(line)

        all_products.append({
            'title': title,
            'base_style_id': base_style,
            'price': regular_price,
            'sale_price': sale_price,
            'variants': variants
        })

    print(f"\nTotal products: {len(all_products)}")
    total_variants = sum(len(p['variants']) for p in all_products)
    total_on_sale = sum(
        1 for p in all_products for v in p['variants'] if v['sale_price']
    )
    print(f"Total variants: {total_variants}")
    print(f"Variants on sale: {total_on_sale}")

    driver.quit()
    return all_products
