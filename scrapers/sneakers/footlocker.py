import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_footlocker():
    """Scrapes Foot Locker's sale page for sneaker deals."""
    print("🔍 Scraping Foot Locker Sales...")
    driver = get_selenium_driver()
    url = "https://www.footlocker.com/sale/mens/shoes"

    try:
        driver.get(url)
        time.sleep(5)  # ✅ Let the page fully load

        # ✅ Scroll multiple times to load more products
        for _ in range(5):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        # ✅ Updated Foot Locker class names for products
        for deal in soup.find_all("div", class_="ProductCard"):
            try:
                name_elem = deal.find("div", class_="ProductCard-name")
                sale_price_elem = deal.find("div", class_="ProductPrice-selling")
                regular_price_elem = deal.find("div", class_="ProductPrice-original")
                link_elem = deal.find("a", class_="ProductCard-link")
                image_elem = deal.find("img", class_="ProductCard-image")

                if not name_elem or not sale_price_elem or not link_elem:
                    continue  # Skip if essential elements are missing

                name = name_elem.text.strip()
                sale_price = sale_price_elem.text.strip().replace("$", "").replace(",", "")
                regular_price = regular_price_elem.text.strip().replace("$", "").replace(",", "") if regular_price_elem else sale_price
                link = "https://www.footlocker.com" + link_elem["href"]
                image = image_elem["src"] if image_elem else ""

                # ✅ Apply promo codes (if applicable)
                final_price, promo = apply_promo_code(float(sale_price), None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Foot Locker",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Foot Locker Scraper Error: {e}")
        return {}

    finally:
        driver.quit()
