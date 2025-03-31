from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from utils.selenium_setup import get_chrome_driver
import time
import traceback

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def scrape_nike_air_max_1():
    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)

    driver.get(NIKE_SEARCH_URL)
    time.sleep(3)

    product_links = []
    try:
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay")))
        for card in cards:
            href = card.get_attribute("href")
            if href and href.startswith("https://www.nike.com/t/"):
                product_links.append(href)
    except Exception as e:
        print("Failed to load product listing page.")
        traceback.print_exc()
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")

    all_deals = []

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(3)

            product = {}

            try:
                title_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2.css-15k04um")))
                product["title"] = title_elem.text
            except:
                product["title"] = "N/A"

            try:
                style_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.description-preview__style-color")))
                product["style_id"] = style_elem.text.strip()
            except:
                product["style_id"] = "N/A"

            try:
                price_container = driver.find_element(By.CSS_SELECTOR, "div.product-price.is--current-price")
                price = price_container.text.strip().replace("$", "")
                product["price"] = float(price)
            except:
                product["price"] = "N/A"

            try:
                sale_price_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price__wrapper div:nth-child(1)")
                sale_price = sale_price_elem.text.strip().replace("$", "")
                product["sale_price"] = float(sale_price) if sale_price else product.get("price", "N/A")
            except:
                product["sale_price"] = product.get("price", "N/A")

            product["variants"] = []

            try:
                swatches = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.css-1a4fh4s button")))
                for swatch in swatches:
                    try:
                        driver.execute_script("arguments[0].click();", swatch)
                        time.sleep(2)

                        variant = {}

                        try:
                            style_elem = driver.find_element(By.CSS_SELECTOR, "div.description-preview__style-color")
                            variant["style_id"] = style_elem.text.strip()
                        except:
                            variant["style_id"] = "N/A"

                        try:
                            price_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price.is--current-price")
                            variant["price"] = float(price_elem.text.replace("$", ""))
                        except:
                            variant["price"] = "N/A"

                        try:
                            reduced_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price__wrapper div:nth-child(1)")
                            reduced_price = reduced_elem.text.strip().replace("$", "")
                            variant["sale_price"] = float(reduced_price) if reduced_price else variant.get("price", "N/A")
                        except:
                            variant["sale_price"] = variant.get("price", "N/A")

                        product["variants"].append(variant)
                    except Exception as inner_e:
                        print("Variant scrape failed.")
                        traceback.print_exc()

            except:
                pass

            print(f"{product['title']} ({product['style_id']})")
            print(f"  Price: ${product['sale_price']} (was ${product['price']})")
            print(f"  Variants: {len(product['variants'])}\n")

            all_deals.append(product)

        except WebDriverException:
            print(f"Failed to scrape {link} due to error:")
            traceback.print_exc()
            continue

    driver.quit()
    return all_deals
