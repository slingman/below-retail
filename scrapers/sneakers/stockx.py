import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver

def scrape_stockx():
    """Scrapes StockX for sneaker prices."""
    print("🔍 Scraping StockX Sneakers...")
    driver = get_selenium_driver()
    url = "https://stockx.com/sneakers"
    
    try:
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="tile"):
            try:
                name = deal.find("div", class_="tile-title").text.strip()
                sale_price = deal.find("div", 
class_="tile-price").text.strip().replace("$", "")
                link = "https://stockx.com" + deal.find("a")["href"]
                image_elem = deal.find("img")
                image = image_elem["src"] if image_elem else ""

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "StockX",
                        "price": float(sale_price),
                        "link": link,
                        "promo": None
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ StockX Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

