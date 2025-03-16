import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils.selenium_setup import get_selenium_driver
from utils.promo_codes import apply_promo_code

def scrape_amazon():
    """Scrapes Amazon's deals page for tech deals."""
    print("🔍 Scraping Amazon Tech Deals...")
    driver = get_selenium_driver()
    url = "https://www.amazon.com/deals"

    try:
        driver.get(url)
        time.sleep(5)

        for _ in range(3):
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        products = {}

        for deal in soup.find_all("div", class_="DealCard-module__dealCardContent_3pCEQ"):
            try:
                name_elem = deal.find("span", class_="DealCard-module__title_2aJjw")
                sale_price_elem = deal.find("span", class_="a-price-whole")
                regular_price_elem = deal.find("span", class_="a-price a-text-price")

                if not name_elem or not sale_price_elem:
                    continue

                name = name_elem.text.strip()
                sale_price = sale_price_elem.text.strip().replace("$", "").replace(",", "")
                regular_price = regular_price_elem.text.strip().replace("$", "").replace(",", "") if regular_price_elem else sale_price
                link = "https://www.amazon.com" + deal.find("a")["href"]
                image = deal.find("img")["src"] if deal.find("img") else ""

                final_price, promo = apply_promo_code(float(sale_price), None)

                products[name] = {
                    "name": name,
                    "image": image,
                    "prices": [{
                        "store": "Amazon",
                        "price": final_price,
                        "link": link,
                        "promo": promo
                    }]
                }
            except Exception:
                continue

        return products

    except Exception as e:
        print(f"❌ Amazon Scraper Error: {e}")
        return {}

    finally:
        driver.quit()
