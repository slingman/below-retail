import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.selenium_setup import get_driver

def get_nike_deals():
    url = "https://www.nike.com/w?q=air+max+1"  # Adjust URL if needed
    driver = get_driver()

    try:
        print(f"🔍 Accessing {url}")
        driver.get(url)
        time.sleep(5)  # Allow time for dynamic content to load

        wait = WebDriverWait(driver, 10)

        # Locate all product cards
        product_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-card"))
        )
        
        print(f"✅ Found {len(product_cards)} products on Nike.")

        deals = []

        for card in product_cards:
            try:
                # Extract product name
                title_element = card.find_element(By.CSS_SELECTOR, ".product-card__title")
                product_name = title_element.text.strip()

                # Extract product price
                try:
                    price_element = card.find_element(By.CSS_SELECTOR, ".product-price")
                    price_text = price_element.text.strip().replace("$", "")
                    price = float(price_text)  # Convert price to float
                except Exception as e:
                    print(f"⚠️ Price extraction failed for {product_name}: {e}")
                    price = None  # Handle cases where price is missing

                # Extract product link
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, "a")
                    product_link = link_element.get_attribute("href")
                except Exception as e:
                    print(f"⚠️ Link extraction failed for {product_name}: {e}")
                    product_link = None  # Handle missing links

                # Store extracted data
                deals.append({
                    "store": "Nike",
                    "name": product_name,
                    "price": price,
                    "link": product_link
                })

            except Exception as e:
                print(f"⚠️ Error processing a product: {e}")

        driver.quit()
        return deals

    except Exception as e:
        print(f"❌ Error scraping Nike: {str(e)}")  # Debug: print full error message
        driver.quit()
        return []

# Test run
if __name__ == "__main__":
    deals = get_nike_deals()
    for deal in deals:
        print(deal)
