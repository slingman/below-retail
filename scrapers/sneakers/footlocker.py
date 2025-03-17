import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver
from utils.promo_codes import apply_promo_code

def extract_style_id(url):
    """Extracts the style ID from a Foot Locker product URL"""
    match = re.search(r'product/.*?/([A-Z0-9]+)\.html$', url)
    return match.group(1) if match else None

def get_footlocker_deals():
    url = "https://www.footlocker.com/en/category/shoes.html"
    driver = get_driver()

    try:
        print(f"🔍 Accessing {url}")
        driver.get(url)
        time.sleep(5)

        wait = WebDriverWait(driver, 10)
        product_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ProductCard")))

        deals = {}

        for card in product_cards:
            try:
                title_element = card.find_element(By.CSS_SELECTOR, ".ProductName-primary")
                product_name = title_element.text.strip()

                try:
                    price_element = card.find_element(By.CSS_SELECTOR, ".ProductPrice")
                    price_text = price_element.text.strip().replace("$", "").replace(",", "")
                    price = float(price_text) if price_text else None
                except:
                    price = None

                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    product_link = link_element.get_attribute("href")
                except:
                    product_link = None

                style_id = extract_style_id(product_link)

                # Convert price to string before applying promo code
                final_price, promo_code = apply_promo_code("Foot Locker", str(price) if price else "0")

                if style_id:
                    deals[style_id] = {
                        "store": "Foot Locker",
                        "name": product_name,
                        "price": price,
                        "final_price": final_price,
                        "promo_code": promo_code,
                        "link": product_link
                    }
                else:
                    print(f"⚠️ No style ID found for {product_name}")

            except Exception as e:
                print(f"❌ Error processing a Foot Locker product: {e}")

        driver.quit()
        return deals

    except Exception as e:
        print(f"❌ Error scraping Foot Locker: {e}")
        driver.quit()
        return {}

if __name__ == "__main__":
    deals = get_footlocker_deals()
    print(deals)
