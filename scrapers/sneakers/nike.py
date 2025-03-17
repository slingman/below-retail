import time
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

NIKE_SEARCH_URL = "https://www.nike.com/w?q=air%20max%201&vst=air%20max%201"

def get_nike_deals():
    """
    Scrapes Nike's website for Air Max 1 deals using Selenium.
    Returns a dictionary where the key is the style_id.
    """
    print("🔍 Searching Nike for Air Max 1...")
    deals = {}

    driver = get_selenium_driver(headless=True)  # Run in headless mode for speed

    try:
        driver.get(NIKE_SEARCH_URL)
        time.sleep(5)  # Allow page to load

        products = driver.find_elements(By.CLASS_NAME, "product-card__body")

        if not products:
            print("⚠️ No products found. Nike may have changed its layout.")
            return {}

        for product in products:
            try:
                name_element = product.find_element(By.CLASS_NAME, "product-card__title")
                price_element = product.find_element(By.CLASS_NAME, "product-price")
                link_element = product.find_element(By.TAG_NAME, "a")

                if not name_element or not price_element or not link_element:
                    continue  # Skip if any essential info is missing

                name = name_element.text.strip()
                price = price_element.text.replace("$", "").strip()
                link = link_element.get_attribute("href")

                # Extract style ID from URL (Nike uses "/STYLE_ID" at the end of the product page URL)
                style_id = link.split("/")[-1] if "/" in link else None

                if style_id and price.replace(".", "").isdigit():  # Ensure valid price
                    deals[style_id] = {
                        "name": name,
                        "style_id": style_id,
                        "image": "",  # Placeholder (we can extract dynamically)
                        "prices": [{"store": "Nike", "price": float(price), "link": link}]
                    }

            except Exception as e:
                print(f"⚠️ Error processing product: {e}")

        print(f"✅ Found {len(deals)} Nike Air Max 1 deals.")
        return deals

    except Exception as e:
        print(f"❌ Nike Scraper Error: {e}")
        return {}

    finally:
        driver.quit()  # Close Selenium driver
