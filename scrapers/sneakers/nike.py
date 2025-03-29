import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from utils.selenium_setup import get_chrome_driver


def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)

    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver.get(search_url)

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay')))
    except TimeoutException:
        print("Timed out waiting for product cards to load.")
        driver.quit()
        return []

    product_links = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
    for card in cards:
        link = card.get_attribute('href')
        if link and link not in product_links:
            product_links.append(link)

    print(f"Found {len(product_links)} product links.\n")

    results = []

    for url in product_links:
        driver.get(url)
        time.sleep(2)

        wait = WebDriverWait(driver, 10)

        # Get title
        try:
            title_el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-2')))
            title = title_el.text.strip()
        except Exception:
            title = "N/A"

        # Get base style ID from URL
        try:
            style_id = url.split("/")[-1]
        except Exception:
            style_id = "N/A"

        # Get price and sale price
        price = "N/A"
        sale_price = None
        try:
            sale_el = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price-reduced"]')
            price_el = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]')
            sale_price = sale_el.text.strip()
            price = price_el.text.strip()
        except Exception:
            try:
                price_el = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]')
                price = price_el.text.strip()
            except Exception:
                pass

        # Get colorway variant buttons
        variant_style_ids = []
        try:
            color_buttons = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div.colorway-container button')))
            for button in color_buttons:
                try:
                    style_data = button.get_attribute("data-style-color")
                    if style_data and style_data != style_id:
                        variant_style_ids.append(style_data)
                except StaleElementReferenceException:
                    continue
        except TimeoutException:
            pass

        results.append({
            "title": title,
            "style_id": style_id,
            "price": price,
            "sale_price": sale_price,
            "variants": variant_style_ids
        })

        print(f"{title} ({style_id})")
        print(f"  Price: {sale_price if sale_price else price}")
        print(f"  Variants: {len(variant_style_ids)}\n")

    driver.quit()
    return results
