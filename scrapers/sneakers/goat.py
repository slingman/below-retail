import time
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

GOAT_SEARCH_URL = "https://www.goat.com/search?query={query}"

def scrape_goat(query):
    print(f"🔍 Searching GOAT for {query}...")

    driver = get_selenium_driver()
    search_url = GOAT_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="GridProductCard"):
        try:
            name = product.find("div", class_="ProductName").text.strip()
            price = product.find("div", class_="ProductPrice").text.strip().replace("$", "")
            link = "https://www.goat.com" + product.find("a")["href"]
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
