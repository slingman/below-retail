from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import create_webdriver
import time

def scrape_nike_air_max_1():
    print("Finding Nike Air Max 1 deals...\n")
    base_url = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"
    driver = create_webdriver()
    deals = []

    try:
        print("Finding product links...")
        driver.get(base_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.product-card__link-overlay'))
        )
        product_links = [el.get_attribute("href") for el in driver.find_elements(By.CSS_SELECTOR, 'a.product-card__link-overlay')]
        print(f"Found {len(product_links)} product links.\n")
    except Exception as e:
        print(f"Failed to extract product links: {e}")
        driver.quit()
        return []

    for link in product_links:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.headline-2'))
            )

            title = driver.find_element(By.CSS_SELECTOR, 'h1.headline-2').text.strip()
            style = driver.find_element(By.CSS_SELECTOR, '.description-preview__style-color').text.strip()
            price_el = driver.find_element(By.CSS_SELECTOR, '[data-test="product-price"]')
            full_price = price_el.text.strip()

            sale_price = None
            if '\n' in full_price:
                regular_price, discounted_price = full_price.split('\n')
                sale_price = discounted_price.strip()
                full_price = regular_price.strip()

            deal = {
                "title": title,
                "style": style,
                "price": full_price,
                "sale_price": sale_price,
                "url": link
            }
            deals.append(deal)
            print(f"✅ {title} ({style}) | {sale_price or full_price}")
        except Exception as e:
            print(f"\nFailed to scrape {link} due to error: {e}\n")

    driver.quit()
    return deals
