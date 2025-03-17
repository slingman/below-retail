import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver
from utils.promo_codes import apply_promo_code

def extract_style_id(url):
    """Extracts the style ID from a Nike product URL"""
    match = re.search(r'/([A-Z0-9]{6}-[A-Z0-9]{3,4})$', url)
    return match.group(1) if match else None

def get_nike_deals():
    search_query = "air max 1"
    url = f"https://www.nike.com/w?q={search_query.replace(' ', '+')}"
    driver = get_driver()

    try:
        print(f"🔍 Accessing {url}")
        driver.get(url)
        time.sleep(5)

        wait = WebDriverWait(driver, 10)

        product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.product-card")))

        deals = {}

        for card in product_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, "div.product-card__title")
                product_name = title_element.text.strip()

                price_element = card.find_element(By.CSS_SELECTOR, "div.product-price")
                price_text = price_element.text.strip().replace("$", "").replace(",", "")
                price = float(price_text) if price_text else None

                link_element = card.find_element(By.TAG_NAME, "a")
                product_link = link_element.get_attribute("href")

                style_id = extract_style_id(product_link)

                # Convert price to string before applying promo code
                final_price, promo_code = apply_promo_code("Nike", str(price) if price else "0")

                if style_id:
                    deals[style_id] = {
                        "store": "Nike",
                        "name": product_name,
                        "price": price,
                        "final_price": final_price,
                        "promo_code": promo_code,
                        "link": product_link
                    }
                else:
                    print(f"⚠️ No style ID found for {product_name}")

            except Exception as e:
                print(f"❌ Error processing a Nike product: {e}")

        driver.quit()
        return deals

    except Exception as e:
        print(f"❌ Error scraping Nike: {e}")
        driver.quit()
        return {}

if __name__ == "__main__":
    deals = get_nike_deals()
    print(deals)
