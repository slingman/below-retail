import time
import json
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q={query}&vst={query}"

def scrape_nike(query):
    print(f"🔍 Searching Nike for {query}...")

    driver = get_selenium_driver()
    search_url = NIKE_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="product-card"):
        try:
            name = product.find("div", class_="product-card__title").text.strip()
            price = product.find("div", class_="product-price").text.strip()
            link = "https://www.nike.com" + product.find("a")["href"]
            image = product.find("img")["src"] if product.find("img") else ""

            results[name] = {
                "name": name,
                "image": image,
                "price": float(price.replace("$", "").replace(",", "")),
                "link": link,
                "promo": None
            }
        except:
            continue

    return results
