import time
from selenium.webdriver.common.by import By
from utils.selenium_setup import get_selenium_driver

FOOTLOCKER_SEARCH_URL = "https://www.footlocker.com/search?query=air%20max%201"

def get_footlocker_deals():
    """
    Scrapes Foot Locker for Air Max 1 deals using Selenium.
    Returns a dictionary where the key is the style_id.
    """
    print("🔍 Searching Foot Locker for Air Max 1...")
    deals = {}

    driver = get_selenium_driver(headless=True)

    try:
        driver.get(FOOTLOCKER_SEARCH_URL)
        time.sleep(5)

        products = driver.find_elements(By.CLASS_NAME, "ProductCard")

        if not products:
            print("⚠️ No products found on Foot Locker.")
            return {}

        for product in products:
            try:
                name_element = product.find_element(By.CLASS_NAME, "ProductCard-title")
                price_element = product.find_element(By.CLASS_NAME, "ProductPrice")
                link_element = product.find_element(By.TAG_NAME, "a")

                # Ensure elements exist before accessing text
                if not name_element or not price_element or not link_element:
                    continue  

                name = name_element.text.strip()
                price = price_element.text.replace("$", "").strip()
                link = link_element.get_attribute("href")

                # Visit product page to extract style ID
                driver.get(link)
                time.sleep(3)

                try:
                    style_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Supplier-sku')]")
                    style_id = style_element.text.split(":")[-1].strip()
                except:
                    print(f"⚠️ Warning: Missing style_id for {name}, skipping.")
                    continue  

                if not style_id or not price.replace(".", "").isdigit():  
                    continue  

                deals[style_id] = {
                    "name": name,
                    "style_id": style_id,
                    "image": "",  # Placeholder
                    "prices": [{"store": "Foot Locker", "price": float(price), "link": link}]
                }

            except Exception as e:
                print(f"⚠️ Error processing product: {e}")

        print(f"✅ Found {len(deals)} Foot Locker Air Max 1 deals.")
        return deals

    except Exception as e:
        print(f"❌ Foot Locker Scraper Error: {e}")
        return {}

    finally:
        driver.quit()
