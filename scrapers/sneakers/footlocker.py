import time
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

FOOTLOCKER_SEARCH_URL = "https://www.footlocker.com/search?q={query}"

def scrape_footlocker(query):
    print(f"🔍 Searching Foot Locker for {query}...")

    driver = get_selenium_driver()
    search_url = FOOTLOCKER_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="ProductCard"):
        try:
            name = product.find("span", class_="ProductName-primary").text.strip()
            price = product.find("span", class_="ProductPrice-final").text.strip().replace("$", "")
            link = "https://www.footlocker.com" + product.find("a")["href"]
            image = product.find("img")["src"] if product.find("img") else ""

            results[name] = {
                "name": name,
                "image": image,
                "price": float(price.replace(",", "")),
                "link": link,
                "promo": None
            }
        except:
            continue

    return results
