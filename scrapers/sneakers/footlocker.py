from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from scrapers.utils.selenium_setup import get_chrome_driver
import time

def get_footlocker_deals():
    """Scrapes Nike Air Max 1 deals from Foot Locker."""
    driver = get_chrome_driver()
    url = "https://www.footlocker.com/search?query=nike%20air%20max%201"

    print(f"\n🔍 Scraping Foot Locker: {url}")
    driver.get(url)
    time.sleep(3)

    deals = []

    try:
        products = driver.find_elements(By.CSS_SELECTOR, "div.ProductCard")

        for product in products:
            try:
                link_element = product.find_element(By.TAG_NAME, "a")
                product_url = link_element.get_attribute("href")
                name = product.find_element(By.CSS_SELECTOR, "div.ProductName-primary").text
                price = product.find_element(By.CSS_SELECTOR, "div.ProductPrice").text

                # Try to fetch style ID if available
                try:
                    style_id_element = product.find_element(By.CSS_SELECTOR, "span.ProductCard-style")
                    style_id = style_id_element.text.split(":")[-1].strip()
                except NoSuchElementException:
                    style_id = "N/A"

                deals.append({
                    "store": "Foot Locker",
                    "name": name,
                    "price": price,
                    "url": product_url,
                    "style_id": style_id
                })

            except (NoSuchElementException, StaleElementReferenceException):
                print("⚠️ Skipping a product due to missing/stale elements")
    
    except TimeoutException:
        print("❌ Foot Locker page failed to load properly.")

    driver.quit()
    return deals
