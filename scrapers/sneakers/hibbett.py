import time
import json
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

def scrape_hibbett(search_term):
    print(f"🔍 Searching Hibbett for {search_term}...")
    driver = get_selenium_driver()
    
    search_url = f"https://www.hibbett.com/search?q={search_term.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(5)  # Allow JS to load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = {}

    for item in soup.find_all("div", class_="product-tile"):
        try:
            name = item.find("a", class_="link-name").text.strip()
            link = "https://www.hibbett.com" + item.find("a", class_="link-name")["href"]
            price = item.find("span", class_="sales").text.strip()
            image = item.find("img")["src"] if item.find("img") else ""

            products[name] = {
                "name": name,
                "price": price,
                "link": link,
                "image": image,
                "store": "Hibbett Sports"
            }
        except Exception:
            continue
    
    driver.quit()
    return products
