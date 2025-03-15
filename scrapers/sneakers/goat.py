import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_goat():
    """Scrapes GOAT's sneaker listings."""
    print("🔍 Scraping GOAT Sneakers...")
    driver = get_selenium_driver()
    url = "https://www.goat.com/sneakers"
    
    try:
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="grid-product"):
            try:
                name = deal.find("div", 
class_="grid-product-title").text.strip()
                sale_price = deal.find("div", 
class_="grid-product-price").text.strip().replace("$", "")
                link = "https://www.goat.com" + deal.find("a")["href"]
                image_elem = deal.find("img")
                image = image_elem["src"] if image_elem else ""

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "GOAT",
                        "price": float(sale_price),
                        "link": link,
                        "promo": None
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ GOAT Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

