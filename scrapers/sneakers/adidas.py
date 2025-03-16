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

        # Scroll to load more products
        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        # ✅ Updated class names for Adidas' new website structure
        for deal in soup.find_all("div", class_="glass-product-card"):
            try:
                name_elem = deal.find("div", class_="glass-product-card__title")
                sale_price_elem = deal.find("div", class_="gl-price-item gl-price-item--sale")
                regular_price_elem = deal.find("div", class_="gl-price-item gl-price-item--crossed")
                link_elem = deal.find("a", class_="glass-product-card__assets-link")
                image_elem = deal.find("img", class_="glass-product-card__image")

                if not name_elem or not sale_price_elem or not link_elem:
                    continue  # Skip if essential elements are missing

                name = name_elem.text.strip()
                sale_price = sale_price_elem.text.strip().replace("$", "").replace(",", "")
                regular_price = regular_price_elem.text.strip().replace("$", "").replace(",", "") if regular_price_elem else sale_price
                link = "https://www.adidas.com" + link_elem["href"]
                image = image_elem["src"] if image_elem else ""

                # Apply promo codes (if applicable)
                final_price, promo = apply_promo_code(float(sale_price), None)

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
