from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.selenium_setup import get_chrome_driver

import time

def scrape_nike_air_max_1():
    base_url = "https://www.nike.com"
    search_url = f"{base_url}/w?q=air+max+1&vst=air+max+1"

    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 10)

    print("Finding product links...")
    driver.get(search_url)
    time.sleep(2)

    try:
        product_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay")))
        product_links = [elem.get_attribute("href") for elem in product_elements if elem.get_attribute("href")]
    except TimeoutException:
        print("Failed to load product elements from listing page.")
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")

    deals = []

    for link in product_links:
        try:
            driver.get(link)
            time.sleep(2)
            title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-5'))).text
            style_id = link.split("/")[-1]

            try:
                current_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-reduced']").text
                original_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price']").text
            except:
                current_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price']").text
                original_price = current_price

            variants = []
            try:
                swatches = driver.find_elements(By.CSS_SELECTOR, "div.css-xf3ahq button")
                for i, swatch in enumerate(swatches):
                    try:
                        swatch.click()
                        time.sleep(1.5)
                        style_text = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.description-preview__style-color"))).text
                        price_box = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price']")
                        price = price_box.text
                        try:
                            sale_price = driver.find_element(By.CSS_SELECTOR, "[data-test='product-price-reduced']").text
                        except:
                            sale_price = price
                        variants.append({
                            "style_id": style_text,
                            "price": price,
                            "sale_price": sale_price
                        })
                    except WebDriverException:
                        continue
            except Exception:
                pass

            deals.append({
                "title": title,
                "style_id": style_id,
                "price": current_price,
                "sale_price": current_price if current_price != original_price else original_price,
                "variants": variants
            })

            print(f"{title} ({style_id})")
            print(f"  Price: {current_price} (was {original_price})")
            print(f"  Variants: {len(variants)}\n")

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")
            continue

    driver.quit()
    return deals
