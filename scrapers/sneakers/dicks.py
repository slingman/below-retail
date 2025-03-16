import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

def scrape_dicks(search_term):
    print(f"🔍 Searching Dick's Sporting Goods for {search_term}...")
    driver = get_selenium_driver()
    
    search_url = f"https://www.dickssportinggoods.com/search/SearchDisplay?searchTerm={search_term.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JS to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = {}

    for item in soup.find_all("div", class_="product"):
        try:
            name = item.find("h2", class_="product-title").text.strip()
            link = "https://www.dickssportinggoods.com" + item.find("a")["href"]
            price = item.find("span", class_="final-price").text.strip()
            image = item.find("img")["src"] if item.find("img") else ""

            products[name] = {
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "store": "Dick's Sporting Goods"
            }
        except Exception:
            continue
    
    driver.quit()
    return products
