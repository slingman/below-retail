import time
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

STOCKX_SEARCH_URL = "https://stockx.com/search?s={query}"

def scrape_stockx(query):
    print(f"🔍 Searching StockX for {query}...")

    driver = get_selenium_driver()
    search_url = STOCKX_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="tile"):
        try:
            name = product.find("p", class_="title").text.strip()
            price = product.find("div", class_="primary").text.strip().replace("$", "")
            link = "https://stockx.com" + product.find("a")["href"]
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
