import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException
from utils.selenium_setup import get_chrome_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(3)

        product_links = []
        product_cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        for card in product_cards:
            href = card.get_attribute("href")
            if href and href not in product_links:
                product_links.append(href)

        print(f"Found {len(product_links)} product links.\n")

        for link in product_links:
            try:
                driver.get(link)
                time.sleep(2)

                try:
                    title = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'h1.headline-2.css-z3go5q'))).text
                except TimeoutException:
                    title = "N/A"

                try:
                    style_id = driver.find_element(
                        By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
                except:
                    style_id = "N/A"

                try:
                    price_el = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                    lines = price_el.text.strip().split('\n')
                    if len(lines) == 2:
                        sale_price, original_price = lines
                    else:
                        sale_price, original_price = lines[0], None
                except:
                    sale_price = original_price = "N/A"

                print(f"{title} ({style_id})")
                if original_price:
                    print(f"  Price: {sale_price} (was {original_price})")
                else:
                    print(f"  Price: {sale_price}")

                variant_data = []

                # Handle variant swatches
                try:
                    swatches = wait.until(EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, '[data-test="colorway-picker"] button')))
                    for i in range(len(swatches)):
                        try:
                            swatches = driver.find_elements(By.CSS_SELECTOR, '[data-test="colorway-picker"] button')
                            driver.execute_script("arguments[0].scrollIntoView(true);", swatches[i])
                            swatches[i].click()
                            time.sleep(1)

                            variant_style = driver.find_element(
                                By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
                            variant_price_el = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                            variant_lines = variant_price_el.text.strip().split('\n')

                            if len(variant_lines) == 2:
                                variant_sale, variant_orig = variant_lines
                            else:
                                variant_sale, variant_orig = variant_lines[0], None

                            variant_data.append({
                                "style_id": variant_style,
                                "sale_price": variant_sale,
                                "original_price": variant_orig
                            })

                        except Exception:
                            continue
                except TimeoutException:
                    pass

                for variant in variant_data:
                    print(f"    Variant: {variant['style_id']}")
                    if variant["original_price"]:
                        print(f"      Price: {variant['sale_price']} (was {variant['original_price']})")
                    else:
                        print(f"      Price: {variant['sale_price']}")

                print(f"  Variants: {len(variant_data)}\n")

                results.append({
                    "title": title,
                    "style_id": style_id,
                    "price": sale_price,
                    "original_price": original_price,
                    "variants": variant_data
                })

            except WebDriverException as e:
                print(f"Error on {link}: {e}")
                continue

    finally:
        driver.quit()

    return results
