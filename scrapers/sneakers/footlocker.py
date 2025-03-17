from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from scrapers.utils import get_driver  # Ensure this is correctly imported

def get_footlocker_deals():
    driver = get_driver()

    try:
        url = "https://www.footlocker.com/search?query=air+max+1"
        driver.get(url)
        sleep(3)  # Allow time for the page to load

        deals = []
        products = driver.find_elements(By.CSS_SELECTOR, ".ProductCard")  # Update selector if necessary

        for product in products:
            try:
                title = product.find_element(By.CSS_SELECTOR, ".ProductCard-name").text
                price = product.find_element(By.CSS_SELECTOR, ".ProductPrice").text
                link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

                deals.append({
                    "title": title,
                    "price": price,
                    "link": link,
                    "store": "Foot Locker"
                })
            except Exception as e:
                print(f"Error extracting product details: {e}")

        return deals

    finally:
        driver.quit()
