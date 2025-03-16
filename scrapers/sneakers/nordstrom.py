import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

def scrape_nordstrom(search_term):
    print(f"🔍 Searching Nordstrom for {search_term}...")
    driver = get_selenium_driver()
    
    search_url = f"https://www.nordstrom.com/sr?keyword={search_term.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JS to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = {}
    
    for item in soup.find_all("article", class_="yR1fY"):
        try:
            name = item.find("h3", class_="UZDE8").text.strip()
            link = "https://www.nordstrom.com" + item.find("a", class_="x0Tbd")["href"]
            price = item.find("span", class_="nTrW1").text.strip()
            image = item.find("img")["src"] if item.find("img") else ""

            products[name] = {
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "store": "Nordstrom"
            }
        except Exception:
            continue
    
    driver.quit()
    return products
