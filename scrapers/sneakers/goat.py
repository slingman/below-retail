import time
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

def scrape_goat(query):
    driver = get_selenium_driver()
    search_url = f"https://www.goat.com/search?query={query.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)

    products = []
    items = driver.find_elements(By.CLASS_NAME, "GridProduct__wrapper")

    for item in items:
        try:
            name = item.find_element(By.CLASS_NAME, "GridProduct__title").text.strip()
            price = item.find_element(By.CLASS_NAME, "GridProduct__price").text.strip().replace('$', '')
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = item.find_element(By.TAG_NAME, "img").get_attribute("src")

            products.append({
                "name": name,
                "store": "GOAT",
                "price": float(price),
                "link": link,
                "image": image,
            })
        except:
            continue

    driver.quit()
    return products
