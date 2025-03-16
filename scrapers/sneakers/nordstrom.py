from utils.selenium_setup import get_selenium_driver
from bs4 import BeautifulSoup
import time

def scrape_nordstrom():
    print("🔍 Scraping Nordstrom...")
    driver = get_selenium_driver()
    driver.get("https://www.nordstrom.com/browse/men/shoes/sale")
    time.sleep(5)  # Allow JavaScript to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    deals = {}
    for product in soup.find_all("div", class_="product-item"):  # Adjust class if needed
        try:
            name = product.find("span", class_="product-title").text.strip()
            price = float(product.find("span", class_="sale-price").text.replace("$", "").strip())
            link = "https://www.nordstrom.com" + product.find("a")["href"]
            image = product.find("img")["src"]
            
            if name not in deals:
                deals[name] = {"name": name, "image": image, "prices": []}
            deals[name]["prices"].append({"store": "Nordstrom", "price": price, "link": link, "promo": None})
        except Exception as e:
            continue
    
    return deals
