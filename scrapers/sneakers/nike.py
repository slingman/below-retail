from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from scrapers.utils.selenium_setup import get_chrome_driver
import time

def get_nike_deals():
    """Scrapes Nike Air Max 1 deals from Nike's website."""
    driver = get_chrome_driver()
    url = "https://www.nike.com/w?q=air+max+1"

    print(f"\n🔍 Accessing Nike deals...\n")
    driver.get(url)
    time.sleep(3)

    deals = []

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "div.product-card")
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, "div.product-card__title").text
                price = product.find_element(By.CSS_SELECTOR, "div.product-price").text
                link = product.find_element(By.TAG_NAME, "a").get_attribute("href")

                try:
                    style_id = product.find_element(By.CSS_SELECTOR, "div.product-card__style-color").text.split(" ")[-1]
                except NoSuchElementException:
                    style_id = "N/A"

                deals.append({
                    "store": "Nike",
                    "name": name,
                    "price": price,
                    "url": link,
                    "style_id": style_id
                })
            except NoSuchElementException:
                print("⚠️ Skipping a product due to missing elements")
    
    except TimeoutException:
        print("❌ Nike page failed to load properly.")

    driver.quit()
    return deals
