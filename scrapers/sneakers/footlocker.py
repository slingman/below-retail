from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from utils.selenium_setup import get_selenium_driver

def get_footlocker_deals():
    driver = get_selenium_driver()

    url = "https://www.footlocker.com/search?query=nike%20air%20max%201"
    driver.get(url)
    time.sleep(5)  # Wait for page load

    deals = []

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "div.ProductCard")
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, "div.ProductCard-name").text
                price = product.find_element(By.CSS_SELECTOR, "div.ProductPrice").text
                product_url = product.find_element(By.CSS_SELECTOR, "a.ProductCard-link").get_attribute("href")

                style_id = "Unknown"  # Foot Locker may not display this directly

                deals.append({
                    "store": "Foot Locker",
                    "name": name,
                    "price": price,
                    "url": product_url,
                    "style_id": style_id
                })
            except Exception as e:
                print(f"⚠️ Skipping a product due to error: {e}")

    except Exception as e:
        print(f"❌ Error fetching Foot Locker deals: {e}")

    driver.quit()
    return deals
