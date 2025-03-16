import time
import requests
from bs4 import BeautifulSoup
from utils.selenium_setup import get_selenium_driver

ADIDAS_SEARCH_URL = "https://www.adidas.com/us/search?q={query}"

def scrape_adidas(query):
    print(f"🔍 Searching Adidas for {query}...")

    driver = get_selenium_driver()
    search_url = ADIDAS_SEARCH_URL.format(query=query.replace(" ", "%20"))
    driver.get(search_url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    results = {}

    for product in soup.find_all("div", class_="gl-product-card"):
        try:
            name = product.find("span", class_="gl-product-card__name").text.strip()
            price = product.find("div", class_="gl-price-item").text.strip().replace("$", "")
            link = "https://www.adidas.com" + product.find("a")["href"]
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
