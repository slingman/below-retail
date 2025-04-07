# scrapers/sneakers/nike.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver


def scrape_nike_air_max_1():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver(headless=False)  # Keep browser visible for debugging
    deals = []

    try:
        print("Finding product links...")
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay")))
        product_links = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        product_urls = list({link.get_attribute("href") for link in product_links})
        print(f"Found {len(product_urls)} product links.\n")

        for idx, url in enumerate(product_urls):
            print(f"Scraping product {idx + 1}: {url}")
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2")))
                time.sleep(1.5)  # Buffer for JS to render

                product_title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text.strip()
                try:
                    base_style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
                except:
                    base_style = "N/A"

                try:
                    price_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']")
                    price_text = price_elem.text.strip()
                    if "\n" in price_text:
                        original, sale = price_text.split("\n")
                    else:
                        original = price_text
                        sale = None
                except:
                    original = sale = None

                base_product = {
                    "title": product_title,
                    "url": url,
                    "style_id": base_style,
                    "price": sale if sale else original,
                    "original_price": original,
                    "sale_price": sale,
                    "variants": []
                }

                # Scrape swatch picker for variants
                variant_links = []
                try:
                    swatches = driver.find_elements(By.CSS_SELECTOR, "div.css-1ehqh5q a")
                    for swatch in swatches:
                        href = swatch.get_attribute("href")
                        if href and href not in variant_links:
                            variant_links.append(href)
                except Exception as e:
                    print(f"Failed to collect swatch variants: {e}")

                for vlink in variant_links:
                    try:
                        driver.get(vlink)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2")))
                        time.sleep(1.5)
                        style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()

                        try:
                            price_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test='product-price']")
                            price_text = price_elem.text.strip()
                            if "\n" in price_text:
                                v_original, v_sale = price_text.split("\n")
                            else:
                                v_original = price_text
                                v_sale = None
                        except:
                            v_original = v_sale = None

                        variant = {
                            "style_id": style,
                            "price": v_sale if v_sale else v_original,
                            "original_price": v_original,
                            "sale_price": v_sale,
                            "url": vlink,
                        }

                        if v_sale:
                            variant["discount_percent"] = round(
                                (1 - float(v_sale.replace("$", "")) / float(v_original.replace("$", ""))) * 100, 1
                            )
                        base_product["variants"].append(variant)
                    except Exception as e:
                        print(f"  Failed to scrape variant {vlink} due to error: {e}")

                deals.append(base_product)
                time.sleep(1)
            except Exception as e:
                print(f"Failed to scrape {url} due to error: {e}\n")

    finally:
        driver.quit()

    # Print summary
    print("\nFinal Nike Air Max 1 Deals:\n")
    for product in deals:
        print(f"{product['title']} ({product['style_id']}) - {product['price']}")
        for variant in product["variants"]:
            print(f"  Variant {variant['style_id']} - {variant['price']} ({variant.get('discount_percent', 0)}% off)")
        print("")

    print("Summary:")
    print(f"  Total unique products: {len(deals)}")
    print(f"  Variants on sale: {sum(len([v for v in p['variants'] if v['sale_price']]) for p in deals)}")
    return deals
