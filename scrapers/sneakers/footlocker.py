import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver
from utils.promo_codes import apply_promo_code

def get_footlocker_deals():
    url = "https://www.footlocker.com/en/category/shoes.html"
    driver = get_driver()

    deals = []
    
    try:
        driver.get(url)
        time.sleep(5)  # Allow time for dynamic content to load

        wait = WebDriverWait(driver, 10)

        product_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ProductCard"))
        )

        for card in product_cards:
            try:
                # Extract product name
                title_element = card.find_element(By.CSS_SELECTOR, ".ProductName-primary")
                product_name = title_element.text.strip()

                # Extract product price
                try:
                    price_element = card.find_element(By.CSS_SELECTOR, ".ProductPrice")
                    price_text = price_element.text.strip().replace("$", "")
                    price = float(price_text)
                except:
                    price = None

                # Extract product link
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    product_link = link_element.get_attribute("href")
                except:
                    product_link = None

                # Apply promo code if available
                final_price, promo_code = apply_promo_code("Foot Locker", price)

                deals.append({
                    "store": "Foot Locker",
                    "name": product_name,
                    "price": price,
                    "final_price": final_price,
                    "promo_code": promo_code,
                    "link": product_link
                })

            except Exception as e:
                print(f"Error processing a product: {e}")

    except Exception as e:
        print(f"Error scraping Foot Locker: {e}")

    finally:
        driver.quit()  # Ensuring WebDriver closes only after everything is done

    return deals

# Test run
if __name__ == "__main__":
    deals = get_footlocker_deals()
    for deal in deals:
        print(deal)
