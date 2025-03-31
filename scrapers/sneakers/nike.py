# scrapers/sneakers/nike.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_chrome_driver

def scrape_nike_air_max_1():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_chrome_driver()
    driver.get(search_url)
    wait = WebDriverWait(driver, 10)

    print("Finding product links...")
    product_links = []
    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay')))
    for card in cards:
        href = card.get_attribute('href')
        if href and href not in product_links:
            product_links.append(href)

    print(f"Found {len(product_links)} product links.\n")

    results = []

    for link in product_links:
        try:
            driver.get(link)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-2')))

            base_title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text.strip()
            all_variants = []

            swatches = driver.find_elements(By.CSS_SELECTOR, '[data-testid="colorways-list"] li input[type="radio"]')

            for i, swatch in enumerate(swatches):
                try:
                    driver.execute_script("arguments[0].click();", swatch)
                    time.sleep(1.5)

                    style = driver.find_element(By.CSS_SELECTOR, 'div.description-preview__style-color').text.strip()
                    full_title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text.strip()

                    try:
                        price_block = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
                        sale_price = price_block.find_element(By.CSS_SELECTOR, '[data-testid="product-price-reduced"]').text.strip()
                        original_price = price_block.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]').text.strip()
                    except:
                        sale_price = None
                        try:
                            original_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]').text.strip()
                        except:
                            original_price = "N/A"

                    variant_data = {
                        "style": style,
                        "title": full_title,
                        "price": original_price,
                        "sale_price": sale_price,
                    }
                    all_variants.append(variant_data)

                except Exception as e:
                    print(f"Failed to scrape variant {i+1} for {link} due to: {e}")
                    continue

            base_style = all_variants[0]["style"] if all_variants else "N/A"
            base_price = all_variants[0]["price"] if all_variants else "N/A"
            base_sale = all_variants[0]["sale_price"] if all_variants else None

            print(f"{base_title} ({base_style})")
            if base_sale:
                print(f"  Price: {base_sale} (was {base_price})")
            else:
                print(f"  Price: {base_price}")
            print(f"  Variants: {len(all_variants)}\n")

            results.append({
                "title": base_title,
                "style": base_style,
                "price": base_price,
                "sale_price": base_sale,
                "variants": all_variants,
            })

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")

    driver.quit()
    return results
