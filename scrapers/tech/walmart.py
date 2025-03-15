import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_walmart():
    """Scrapes Walmart's electronics clearance page."""
    print("🔍 Scraping Walmart Tech Deals...")
    driver = get_selenium_driver()
    url = "https://www.walmart.com/cp/electronics-clearance/1078524"

    try:
        driver.get(url)
        time.sleep(5)

        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", 
class_="search-result-gridview-item"):
            try:
                name_elem = deal.find("a", class_="product-title-link")
                sale_price_elem = deal.find("span", 
class_="price-characteristic")
                regular_price_elem = deal.find("span", 
class_="price-mantle")

                if not name_elem or not sale_price_elem:
                    continue  # Skip if required elements are missing

                name = name_elem.text.strip()
                sale_price = sale_price_elem.text.strip().replace("$", 
"").replace(",", "")
                regular_price = 
regular_price_elem.text.strip().replace("$", "").replace(",", "") if 
regular_price_elem else sale_price

                link_elem = deal.find("a", class_="product-title-link")
                link = "https://www.walmart.com" + link_elem["href"] if 
link_elem else "#"

                image_elem = deal.find("img")
                image = image_elem["src"] if image_elem else ""

                final_price, promo = apply_promo_code(float(sale_price), 
None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Walmart",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Walmart Scraper Error: {e}")
        return {}

    finally:
        driver.quit()

