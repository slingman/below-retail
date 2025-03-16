import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

def scrape_stockx(search_term):
    print(f"🔍 Searching StockX for {search_term}...")
    driver = get_selenium_driver()
    
    search_url = f"https://stockx.com/search?s={search_term.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JS to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = {}

    for item in soup.find_all("div", class_="css-1oxq7lt"):
        try:
            name = item.find("p", class_="css-3lpefb").text.strip()
            link = "https://stockx.com" + item.find("a")["href"]
            price = item.find("div", class_="css-16my406").text.strip()
            image = item.find("img")["src"] if item.find("img") else ""

            products[name] = {
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "store": "StockX"
            }
        except Exception:
            continue
    
    driver.quit()
    return products
