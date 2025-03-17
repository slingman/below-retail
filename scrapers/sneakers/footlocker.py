from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from utils.selenium_setup import get_driver
import time

def get_footlocker_deals():
    driver = get_driver()
    driver.get("https://www.footlocker.com/search?query=nike%20air%20max%201")

    deals = []

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ProductCard"))
        )
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductCard")

        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, ".ProductName-primary").text.strip()
                link = product.find_element(By.CSS_SELECTOR, ".ProductCard-link").get_attribute("href")

                # Price extraction with multiple fallback options
                try:
                    price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice-final").text.strip()
                except NoSuchElementException:
                    try:
                        price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice-original").text.strip()
                    except NoSuchElementException:
                        try:
                            price_final = product.find_element(By.CSS_SELECTOR, ".ProductPrice").text.strip()
                        except NoSuchElementException:
                            price_final = "Price not found"

                deals.append({
                    "name": name,
                    "price_final": price_final,
                    "link": link
                })

            except NoSuchElementException:
                continue  # Skip products that don't have the necessary elements

    except Exception as e:
        print(f"Error scraping Foot Locker: {e}")

    driver.quit()
    return deals
