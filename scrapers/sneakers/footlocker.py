import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver
from utils.promo_code import apply_promo_code

def scrape_footlocker():
    url = "https://www.footlocker.com/en/category/shoes.html"  # Update URL if needed
    driver = get_driver()

    try:
        driver.get(url)
        time.sleep(5)  # Allow time for dynamic content to load

        wait = WebDriverWait(driver, 10)

        # Get all product cards
        product_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".ProductCard"))
        )

        deals = []

        for card in product_cards:
            try:
                # Extract product name
                title_element = card.find_element(By.CSS_SELECTOR, ".ProductName-primary")
                product_name = title_element.text.strip()

                # Extract product price
                try:
                    price_element = card.find_element(By.CSS_SELECTOR, ".ProductPrice")
                    price_text = price_element.text.strip().replace("$", "")
                    price = float(price_text)  # Convert price to float
                except:
                    price = None  # Handle cases where price is missing

                # Extract product link
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    product_link = link_element.get_attribute("href")
                except:
                    product_link = None  # Handle missing links

                # Check for applicable promo codes
                final_price, promo_code = apply_promo_code("Foot Locker", price)

                # Store extracted data
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

        driver.quit()
        return deals

    except Exception as e:
        print(f"Error scraping Foot Locker: {e}")
        driver.quit()
        return []

# Test run
if __name__ == "__main__":
    deals = scrape_footlocker()
    for deal in deals:
        print(deal)
