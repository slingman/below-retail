import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from utils.selenium_setup import get_chrome_driver

BASE_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)
    all_products = []

    try:
        driver.get(BASE_URL)
        time.sleep(3)

        product_links = []
        product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product-card')))
        for card in product_cards:
            try:
                link = card.find_element(By.CSS_SELECTOR, 'a.product-card__link-overlay')
                href = link.get_attribute('href')
                if href not in product_links:
                    product_links.append(href)
            except Exception:
                continue

        print(f"Found {len(product_links)} product links.\n")

        for url in product_links:
            try:
                driver.get(url)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
                time.sleep(1.5)  # Give the page some breathing room

                # Get style ID from URL
                try:
                    style_id = url.split("/")[-1].split('?')[0]
                except Exception:
                    style_id = "N/A"

                # Get title
                try:
                    title_el = wait.until(EC.presence_of_element_located((
                        By.CSS_SELECTOR, "h1[class*='headline']")))
                    title = title_el.text.strip()
                except Exception:
                    title = "N/A"

                # Get price and sale price
                price = "N/A"
                sale_price = None
                try:
                    price_el = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price-reduced']")
                    reg_price_el = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
                    price = reg_price_el.text.strip()
                    sale_price = price_el.text.strip()
                except Exception:
                    try:
                        price_el = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
                        price = price_el.text.strip()
                    except Exception:
                        pass

                # Get colorway variants
                variant_style_ids = []
                sale_count = 0
                try:
                    color_buttons = wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, 'div.css-1ajgutz a')))
                    for btn in color_buttons:
                        try:
                            variant_url = btn.get_attribute('href')
                            if not variant_url or variant_url == url:
                                continue

                            variant_style = variant_url.split('/')[-1].split('?')[0]
                            if variant_style not in variant_style_ids:
                                variant_style_ids.append(variant_style)
                        except StaleElementReferenceException:
                            continue
                except TimeoutException:
                    pass

                product = {
                    "title": title,
                    "style_id": style_id,
                    "price": price,
                    "sale_price": sale_price,
                    "variant_style_ids": variant_style_ids
                }

                print(f"{title} ({style_id})")
                print(f"  Price: {price}" + (f" → {sale_price}" if sale_price else ""))
                print(f"  Variants: {len(variant_style_ids)}\n")

                all_products.append(product)

            except Exception as e:
                print(f"Failed to process {url}: {e}")
                continue

    finally:
        driver.quit()

    return all_products
