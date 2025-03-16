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
        time.sleep(7)  # ✅ Let the page fully load (GOAT is JavaScript-heavy)

        # ✅ Scroll down slowly to force content load
        for _ in range(8):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        # ✅ Updated selectors for GOAT's new structure
        for deal in soup.find_all("div", class_="GridCell"):
            try:
                name_elem = deal.find("p", class_="ProductCard__title")
                price_elem = deal.find("span", class_="ProductCard__price")
                link_elem = deal.find("a", class_="ProductCard__link")
                image_elem = deal.find("img", class_="ProductCard__image")

                if not name_elem or not price_elem or not link_elem:
                    continue  # Skip if essential elements are missing

                name = name_elem.text.strip()
                price = price_elem.text.strip().replace("$", "").replace(",", "")
                link = "https://www.goat.com" + link_elem["href"]
                image = image_elem["src"] if image_elem else ""

                # ✅ Apply promo codes (if applicable)
                final_price, promo = apply_promo_code(float(price), None)

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
