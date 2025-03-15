import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_adidas():
    """Scrapes Adidas' sale page for sneaker deals."""
    print("🔍 Scraping Adidas Sales...")
    driver = get_selenium_driver()
    url = "https://www.adidas.com/us/sale"
    
    try:
        driver.get(url)
        time.sleep(5)

        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="glass-product-card"):
            try:
                name = deal.find("div", 
class_="glass-product-card__title").text.strip()
                sale_price = deal.find("div", 
class_="gl-price-item--sale").text.strip().replace("$", "")
                regular_price_elem = deal.find("div", 
class_="gl-price-item--crossed")
                regular_price = 
regular_price_elem.text.strip().replace("$", "") if regular_price_elem else 
sale_price
                link = "https://www.adidas.com" + deal.find("a")["href"]
                image_elem = deal.find("img")
                image = image_elem["src"] if image_elem else ""

                final_price, promo = apply_promo_code(float(sale_price), 
None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Adidas",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Adidas Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

