from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from utils.selenium_setup import get_selenium_driver

def get_nike_deals():
    driver = get_selenium_driver()

    url = "https://www.nike.com/w?q=air+max+1"
    driver.get(url)
    time.sleep(5)  # Wait for the page to load

    deals = []

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-card")
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, "div.product-card__title").text
                price = product.find_element(By.CSS_SELECTOR, "div.product-price").text
                product_url = product.find_element(By.CSS_SELECTOR, "a.product-card__link-overlay").get_attribute("href")

                style_id_element = product.find_element(By.CSS_SELECTOR, "div.product-card__style-color")
                style_id = style_id_element.text.split(" ")[-1] if style_id_element else "Unknown"

                deals.append({
                    "store": "Nike",
                    "name": name,
                    "price": price,
                    "url": product_url,
                    "style_id": style_id
                })
            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    except Exception as e:
        print(f"❌ Error fetching Nike deals: {e}")

    driver.quit()
    return deals
