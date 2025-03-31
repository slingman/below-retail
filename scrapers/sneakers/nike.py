from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.selenium_setup import get_chrome_driver
import time

def scrape_nike_air_max_1():
    search_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = get_chrome_driver()
    driver.get(search_url)

    wait = WebDriverWait(driver, 10)
    product_links = []

    # Wait for product cards to load and collect their hrefs
    try:
        product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-card__link-overlay")))
        product_links = [card.get_attribute("href") for card in product_cards if card.get_attribute("href")]
    except TimeoutException:
        print("Timeout: Failed to load product cards")

    print(f"Found {len(product_links)} product links.\n")

    deals = []

    for url in product_links:
        try:
            driver.get(url)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.headline-2.css-15xq6wr")))

            title = driver.find_element(By.CSS_SELECTOR, "h1.headline-2.css-15xq6wr").text.strip()
            try:
                base_style = driver.find_element(By.CSS_SELECTOR, "div.description-preview__style-color").text.strip().split(" ")[-1]
            except:
                base_style = "N/A"

            try:
                price_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]")
                full_price = price_elem.find_element(By.CSS_SELECTOR, "div.css-0").text.strip()
                sale_price = price_elem.find_element(By.CSS_SELECTOR, "div[data-test=product-price-reduced]").text.strip()
            except:
                try:
                    sale_price = "N/A"
                    full_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]").text.strip()
                except:
                    full_price = "N/A"
                    sale_price = "N/A"

            variants = []
            try:
                swatches = driver.find_elements(By.CSS_SELECTOR, "li.product-variants__colorway")
                for swatch in swatches:
                    try:
                        swatch.click()
                        time.sleep(1)  # Give it a sec to load
                        style = driver.find_element(By.CSS_SELECTOR, "div.description-preview__style-color").text.strip().split(" ")[-1]
                        try:
                            price_wrap = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]")
                            current_price = price_wrap.find_element(By.CSS_SELECTOR, "div.css-0").text.strip()
                            reduced_price = price_wrap.find_element(By.CSS_SELECTOR, "div[data-test=product-price-reduced]").text.strip()
                        except:
                            current_price = driver.find_element(By.CSS_SELECTOR, "div[data-test=product-price]").text.strip()
                            reduced_price = "N/A"
                        variants.append({
                            "style_id": style,
                            "price": current_price,
                            "sale_price": reduced_price
                        })
                    except Exception as e:
                        continue
            except:
                pass

            deals.append({
                "title": title,
                "base_style_id": base_style,
                "price": full_price,
                "sale_price": sale_price,
                "url": url,
                "variants": variants
            })

            print(f"{title} ({base_style})")
            print(f"  Price: {sale_price if sale_price != 'N/A' else full_price}")
            print(f"  Variants: {len(variants)}")
            print()
        except Exception as e:
            print(f"Failed to scrape {url} due to error: {e}\n")
            continue

    driver.quit()
    return deals
