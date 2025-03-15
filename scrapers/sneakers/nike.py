import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_nike():
    """Scrapes Nike's sale page for sneaker deals."""
    print("🔍 Scraping Nike Sales...")
    driver = get_selenium_driver()
    url = "https://www.nike.com/w/sale-3yaep"
    
    try:
        driver.get(url)
        time.sleep(5)

        # Scroll to load more items
        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="product-card"):
            try:
                name = deal.find("div", 
class_="product-card__title").text.strip()
                sale_price = deal.find("div", {"data-testid": 
"product-price-reduced"}).text.strip().replace("$", "")
                regular_price = deal.find("div", {"data-testid": 
"product-price"}).text.strip().replace("$", "")
                link = deal.find("a", 
class_="product-card__link-overlay")["href"]
                image = deal.find("img", 
class_="product-card__hero-image")["src"]
                
                final_price, promo = apply_promo_code(float(sale_price), 
None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Nike",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Nike Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

