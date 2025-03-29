import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from utils.selenium_setup import get_chrome_driver


def extract_price_info(price_container):
    try:
        current_price_elem = price_container.find_element(By.CSS_SELECTOR, ".product-price.is--current-price")
        current_price = current_price_elem.text.strip().replace("$", "")
        current_price = float(current_price)
    except NoSuchElementException:
        current_price = None

    try:
        original_price_elem = price_container.find_element(By.CSS_SELECTOR, ".product-price.us__styling")
        original_price = original_price_elem.text.strip().replace("$", "")
        original_price = float(original_price)
    except NoSuchElementException:
        original_price = current_price

    return current_price, original_price


def scrape_product_detail(driver, url):
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Wait for product title and base style ID
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-5.css-15k3avv"))).text.strip()
        style_id = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.description-preview__style-color"))).text.strip()

        # Wait for price
        price_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-price__wrapper")))
        price, original_price = extract_price_info(price_container)

        base_product = {
            "title": title,
            "style_id": style_id,
            "price": price,
            "original_price": original_price,
            "variants": [],
        }

        # Colorway variants
        variant_buttons = driver.find_elements(By.CSS_SELECTOR, "li.css-xf3ahq input[type='radio']")
        variant_urls = []

        for btn in variant_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)
                current_url = driver.current_url
                if current_url not in variant_urls:
                    variant_urls.append(current_url)
            except Exception:
                continue

        # Visit each colorway variant
        for variant_url in variant_urls:
            driver.get(variant_url)
            time.sleep(1)
            try:
                variant_style = driver.find_element(By.CSS_SELECTOR, "div.description-preview__style-color").text.strip()
                price_container = driver.find_element(By.CSS_SELECTOR, "div.product-price__wrapper")
                price, original_price = extract_price_info(price_container)
                variant_info = {
                    "style_id": variant_style,
                    "price": price,
                    "original_price": original_price,
                }
                base_product["variants"].append(variant_info)
            except Exception:
                continue

        return base_product

    except Exception as e:
        print(f"Failed to scrape product page: {url} — {e}")
        return None


def scrape_nike_air_max_1():
    driver = get_chrome_driver(headless=True)
    wait = WebDriverWait(driver, 15)
    results = []

    try:
        search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
        driver.get(search_url)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay")))
        time.sleep(2)

        product_links = list({
            a.get_attribute("href")
            for a in driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        })

        print(f"Found {len(product_links)} product links.\n")

        for url in product_links:
            product_data = scrape_product_detail(driver, url)
            if product_data:
                print(f"{product_data['title']} ({product_data['style_id']})")
                if product_data["price"] and product_data["original_price"]:
                    print(f"  Price: ${product_data['price']} (was ${product_data['original_price']})")
                else:
                    print(f"  Price: N/A")

                print(f"  Variants: {len(product_data['variants'])}")
                for variant in product_data["variants"]:
                    price_str = f"${variant['price']}" if variant['price'] else "N/A"
                    orig_str = f"(was ${variant['original_price']})" if variant['original_price'] and variant['original_price'] > variant['price'] else ""
                    print(f"    - {variant['style_id']}: {price_str} {orig_str}")
                print("")
                results.append(product_data)

    finally:
        driver.quit()

    return results
