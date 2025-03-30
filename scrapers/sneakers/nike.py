import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from utils.selenium_setup import get_chrome_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(3)  # Let the page load

        product_links = []
        product_cards = driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')
        for card in product_cards:
            href = card.get_attribute("href")
            if href and href not in product_links:
                product_links.append(href)

        print(f"Found {len(product_links)} product links.\n")

        for link in product_links:
            driver.get(link)
            time.sleep(2)  # let product page load

            try:
                title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-2.css-z3go5q'))).text
            except TimeoutException:
                title = "N/A"

            try:
                style_id = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
            except:
                style_id = "N/A"

            try:
                price_container = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                price_text = price_container.text.split('\n')
                if len(price_text) == 2:
                    sale_price = price_text[0]
                    original_price = price_text[1]
                else:
                    sale_price = price_text[0]
                    original_price = None
            except:
                sale_price = original_price = "N/A"

            print(f"{title} ({style_id})")
            print(f"  Price: {sale_price if original_price is None else f'{sale_price} (was {original_price})'}")

            # Now get all colorway variants
            variant_data = []
            try:
                swatches = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '[data-test="colorway-picker"] button')))
                for i in range(len(swatches)):
                    try:
                        swatches = driver.find_elements(By.CSS_SELECTOR, '[data-test="colorway-picker"] button')
                        swatches[i].click()
                        time.sleep(1)

                        variant_style_id = driver.find_element(By.CSS_SELECTOR, '[data-test="product-style-colorway"]').text.strip()
                        variant_price_el = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
                        variant_price_lines = variant_price_el.text.split('\n')

                        if len(variant_price_lines) == 2:
                            variant_sale = variant_price_lines[0]
                            variant_original = variant_price_lines[1]
                        else:
                            variant_sale = variant_price_lines[0]
                            variant_original = None

                        variant_data.append({
                            "style_id": variant_style_id,
                            "sale_price": variant_sale,
                            "original_price": variant_original
                        })
                    except StaleElementReferenceException:
                        continue
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

    finally:
        driver.quit()

    return results
