import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from scrapers.utils.selenium_utils import get_driver


FOOTLOCKER_URL = "https://www.footlocker.com/search?query=air%20max%201"


def get_footlocker_deals():
    driver = get_driver()
    driver.get(FOOTLOCKER_URL)
    time.sleep(5)  # Allow time for dynamic content to load

    deals = []

    # Scroll to the bottom of the page to load more products
    for _ in range(3):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    product_cards = driver.find_elements(By.CLASS_NAME, "ProductCard")

    for card in product_cards:
        try:
            # Extract product name
            name_element = card.find_element(By.CLASS_NAME, "ProductName-primary")
            name = name_element.text.strip()

            # Extract product link
            link_element = card.find_element(By.CLASS_NAME, "ProductCard-link")
            link = link_element.get_attribute("href")

            # Extract final price
            try:
                price_final_element = card.find_element(By.CLASS_NAME, "ProductPrice-final")
                price_final = price_final_element.text.strip()
            except NoSuchElementException:
                price_final = "Price not found"

            # Extract original price (if available)
            try:
                price_original_element = card.find_element(By.CLASS_NAME, "ProductPrice-original")
                price_original = price_original_element.text.strip()
            except NoSuchElementException:
                price_original = price_final  # If no original price, assume it's the same as the final price

            deals.append({
                "name": name,
                "price_final": price_final,
                "price_original": price_original,
                "link": link
            })
        except NoSuchElementException:
            continue

    driver.quit()
    return deals
