from utils.selenium_setup import get_selenium_driver
from bs4 import BeautifulSoup
import time

def scrape_hibbett():
    print("🔍 Scraping Hibbett Sports...")
    driver = get_selenium_driver()
    driver.get("https://www.hibbett.com/sale/mens/shoes/")
    time.sleep(5)  # Allow JavaScript to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    deals = {}
    for product in soup.find_all("div", class_="product-tile"):  # Adjust class if needed
        try:
            name = product.find("a", class_="link").text.strip()
            price = float(product.find("span", class_="sales").text.replace("$", "").strip())
            link = "https://www.hibbett.com" + product.find("a", class_="link")["href"]
            image = product.find("img")["src"]
            
            if name not in deals:
                deals[name] = {"name": name, "image": image, "prices": []}
            deals[name]["prices"].append({"store": "Hibbett", "price": price, "link": link, "promo": None})
        except Exception as e:
            continue
    
    return deals
