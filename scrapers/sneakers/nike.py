import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_chrome_driver


def extract_price_info(price_container):
    try:
        sale_price = price_container.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price-reduced"]').text
        original_price = price_container.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]').text
        return original_price, sale_price
    except:
        try:
            original_price = price_container.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]').text
            return original_price, None
        except:
            return None, None


def extract_variant_info(driver):
    variants = []
    wait = WebDriverWait(driver, 10)

    try:
        color_buttons = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, '[data-testid="product-variant-colorway-btn"]')
        ))
    except:
        return variants  # No variants found

    for button in color_buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)

            style_id = None
            try:
                style_id = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="product-style-colorway"] span').text.strip()
            except:
                pass

            price_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
            original_price, sale_price = extract_price_info(price_container)

            variants.append({
                'style_id': style_id,
                'original_price': original_price,
                'sale_price': sale_price
            })
        except Exception:
            continue

    return variants


def scrape_nike_air_max_1():
    url = "https://www.nike.com/w?q=air%20max%201"
    driver = get_chrome_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    product_links = []
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay')))
        product_anchors = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        product_links = list({a.get_attribute("href") for a in product_anchors})
    except:
        print("Failed to retrieve product links.")
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")

    all_products = []

    for link in product_links:
        driver.get(link)
        time.sleep(2)
        wait = WebDriverWait(driver, 10)

        try:
            title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-title"]'))).text.strip()
        except:
            title = "N/A"

        try:
            style_id = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="product-style-colorway"] span').text.strip()
        except:
            style_id = "N/A"

        try:
            price_container = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
            original_price, sale_price = extract_price_info(price_container)
        except:
            original_price = sale_price = None

        try:
            variants = extract_variant_info(driver)
        except:
            variants = []

        print(f"{title} ({style_id})")
        if sale_price:
            print(f"  Price: {sale_price} (was {original_price})")
        else:
            print(f"  Price: {original_price or 'N/A'}")

        print(f"  Variants: {len(variants)}\n")

        all_products.append({
            'title': title,
            'style_id': style_id,
            'original_price': original_price,
            'sale_price': sale_price,
            'variants': variants
        })

    driver.quit()
    return all_products
