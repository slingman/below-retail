import time
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

HIBBETT_SEARCH_URL = "https://www.hibbett.com/search?q={query}"

def scrape_hibbett(query):
    print(f"🔍 Searching Hibbett for {query}...")

    driver = get_selenium_driver()
    search_url = HIBBETT_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="product-tile"):
        try:
            name = product.find("a", class_="product-title").text.strip()
            price = product.find("span", class_="sales").text.strip().replace("$", "")
            link = "https://www.hibbett.com" + product.find("a")["href"]
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
