import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from utils.selenium_setup import create_webdriver


def scrape_nike_air_max_1():
    print("Finding product links...")

    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()
    driver.get(search_url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.product-card__link-overlay")))
        product_elements = driver.find_elements(By.CSS_SELECTOR, "a.product-card__link-overlay")
        product_links = list({elem.get_attribute("href") for elem in product_elements if elem.get_attribute("href")})
    except Exception as e:
        print(f"Failed to extract product links: {e}")
        driver.quit()
        return []

    print(f"Found {len(product_links)} product links.\n")

    all_deals = []

    for link in product_links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".description-preview__style-color"))
            )

            product_title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text.strip()
            style_id = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
            price_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price span[aria-hidden='true']")
            base_price = price_elem.text.strip().replace("$", "").replace(",", "")
            base_sale = None

            try:
                sale_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price s")
                base_sale = sale_elem.text.strip().replace("$", "").replace(",", "")
            except:
                pass  # no sale price

            variants = []

            try:
                swatches = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li.css-1ehqh5q a")))
            except TimeoutException:
                swatches = []

            for swatch in swatches:
                try:
                    driver.execute_script("arguments[0].click();", swatch)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".description-preview__style-color"))
                    )
                    time.sleep(1.5)

                    style = driver.find_element(By.CSS_SELECTOR, ".description-preview__style-color").text.strip()
                    title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2").text.strip()
                    price = driver.find_element(By.CSS_SELECTOR, "div.product-price span[aria-hidden='true']").text.strip().replace("$", "").replace(",", "")

                    sale = None
                    try:
                        sale_elem = driver.find_element(By.CSS_SELECTOR, "div.product-price s")
                        sale = sale_elem.text.strip().replace("$", "").replace(",", "")
                    except:
                        pass

                    variant = {
                        "style_id": style,
                        "title": title,
                        "price": float(price),
                        "sale_price": float(sale) if sale else None,
                        "link": driver.current_url
                    }
                    variants.append(variant)
                except Exception as err:
                    print(f"Variant scrape failed on {link}: {err}")
                    continue

            print(f"{product_title} ({style_id})")
            print(f"Base price: ${base_price}")
            if base_sale:
                print(f"Base sale: ${base_sale}")
            print(f"Variants found: {len(variants)}")
            for var in variants:
                print(f" - {var['style_id']}: ${var['price']}" + (f" → ${var['sale_price']}" if var['sale_price'] else ""))
            print()

            all_deals.extend(variants)

        except Exception as e:
            print(f"Failed to scrape {link} due to error: {e}\n")
            continue

    driver.quit()
    return all_deals
