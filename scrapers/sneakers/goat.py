import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_goat():
    """Scrapes GOAT's sneaker deals."""
    print("🔍 Scraping GOAT Sneakers...")
    driver = get_selenium_driver()
    url = "https://www.goat.com/sneakers"

    try:
        driver.get(url)
        time.sleep(5)  # ✅ Let the page fully load

        # ✅ Scroll multiple times to load more products
        for _ in range(5):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        # ✅ Updated GOAT class names for product cards
        for deal in soup.find_all("div", class_="GridCell"):
            try:
                name_elem = deal.find("div", class_="ProductCard__title")
                sale_price_elem = deal.find("div", class_="ProductCard__price")
                link_elem = deal.find("a", class_="ProductCard__link")
                image_elem = deal.find("img", class_="ProductCard__image")

                if not name_elem or not sale_price_elem or not link_elem:
                    continue  # Skip if essential elements are missing

                name = name_elem.text.strip()
                sale_price = sale_price_elem.text.strip().replace("$", "").replace(",", "")
                link = "https://www.goat.com" + link_elem["href"]
                image = image_elem["src"] if image_elem else ""

                # ✅ Apply promo codes (if applicable)
                final_price, promo = apply_promo_code(float(sale_price), None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "GOAT",
                        "price": final_price,
                        "link": link,
                        "promo": promo
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
