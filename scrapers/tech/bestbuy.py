import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_bestbuy():
    """Scrapes Best Buy's tech deals page."""
    print("🔍 Scraping Best Buy Tech Deals...")
    driver = get_selenium_driver()
    url = "https://www.bestbuy.com/site/top-deals"
    
    try:
        driver.get(url)
        time.sleep(5)

        # Scroll to load more items
        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="sku-item"):
            try:
                name = deal.find("h4", class_="sku-header").text.strip()
                sale_price = deal.find("div", 
class_="priceView-hero-price").text.strip().replace("$", "")
                regular_price_elem = deal.find("div", 
class_="pricing-price__regular-price")
                regular_price = 
regular_price_elem.text.strip().replace("$", "") if regular_price_elem else 
sale_price
                link = "https://www.bestbuy.com" + deal.find("a")["href"]
                image_elem = deal.find("img")
                image = image_elem["src"] if image_elem else ""

                final_price, promo = apply_promo_code(float(sale_price), 
None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Best Buy",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Best Buy Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

