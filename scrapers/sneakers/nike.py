# scrapers/sneakers/nike.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from utils.selenium_setup import create_webdriver
import time


def extract_price_block(driver):
    try:
        price_container = driver.find_element(By.CLASS_NAME, "product-price")
        sale_price = price_container.find_element(By.CLASS_NAME, "is--current-price").text
        try:
            full_price = price_container.find_element(By.CLASS_NAME, "is--striked").text
        except NoSuchElementException:
            full_price = sale_price
        return full_price, sale_price
    except Exception:
        return "N/A", "N/A"


def scrape_nike_air_max_1():
    driver = create_webdriver()
    driver.get("https://www.nike.com/w?q=air%20max%201&vst=air%20max%201")

    print("Finding product links...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card__link-overlay"))
        )
    except TimeoutException:
        print("Timeout while waiting for product cards.")
        driver.quit()
        return []

    links = []
    seen = set()
    cards = driver.find_elements(By.CLASS_NAME, "product-card__link-overlay")
    for card in cards:
        href = card.get_attribute("href")
        if href and href not in seen:
            links.append(href)
            seen.add(href)

    print(f"Found {len(links)} product links.\n")

    all_products = []

    for link in links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product-title"))
            )

            title = driver.find_element(By.CLASS_NAME, "product-title").text
            style_id = driver.find_element(By.CLASS_NAME, "description-preview__style-color").text
            full_price, sale_price = extract_price_block(driver)

            print(f"{title} ({style_id})")
            if sale_price != full_price:
                print(f"  🔥 {sale_price} (was {full_price})")
            else:
                print(f"  {full_price}")

            variants = []
            swatches = driver.find_elements(By.CSS_SELECTOR, '[data-qa="colorway-image"]')
            for i, swatch in enumerate(swatches):
                try:
                    driver.execute_script("arguments[0].click();", swatch)
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(driver.find_element(By.CLASS_NAME, "product-title"))
                    )
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "product-title"))
                    )
                    time.sleep(1)

                    variant_style = driver.find_element(By.CLASS_NAME, "description-preview__style-color").text
                    full_price_v, sale_price_v = extract_price_block(driver)
                    is_sale = full_price_v != sale_price_v

                    if variant_style != style_id:
                        variants.append({
                            "style_id": variant_style,
                            "price": sale_price_v,
                            "full_price": full_price_v,
                            "on_sale": is_sale,
                        })
                except Exception:
                    continue

            for v in variants:
                price_str = f"  🔥 {v['price']} (was {v['full_price']})" if v['on_sale'] else f"  {v['price']}"
                print(f"    Variant: {v['style_id']} - {price_str}")

            print()
            all_products.append({
                "title": title,
                "style_id": style_id,
                "price": sale_price,
                "full_price": full_price,
                "on_sale": sale_price != full_price,
                "variants": variants,
                "url": link,
            })

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")
            continue

    driver.quit()

    print("Final Nike Air Max 1 Deals:\n")
    for product in all_products:
        print(f"{product['title']} ({product['style_id']})")
        if product["on_sale"]:
            print(f"  🔥 {product['price']} (was {product['full_price']})")
        else:
            print(f"  {product['price']}")
        for v in product["variants"]:
            price_str = f"  🔥 {v['price']} (was {v['full_price']})" if v['on_sale'] else f"  {v['price']}"
            print(f"    Variant: {v['style_id']} - {price_str}")
        print()

    print("Summary:")
    print(f"  Total unique products: {len(all_products)}")
    variant_count = sum(len(p["variants"]) for p in all_products)
    sale_count = sum(
        (1 if p["on_sale"] else 0) + sum(1 for v in p["variants"] if v["on_sale"])
        for p in all_products
    )
    print(f"  Total colorway variants: {variant_count}")
    print(f"  Variants on sale: {sale_count}")

    return all_products
